import json
from decimal import Decimal, InvalidOperation
import pandas as pd
from core.models import *
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ProductForm
from django.utils import timezone
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderInsufficientPrivileges
from django.db import transaction
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.db.models.functions import ExtractYear, ExtractMonth
import time
import logging

@login_required(login_url='/login/')
def analytics(request):
    from django.db.models import Sum, Count, Avg, F, Q
    from django.db.models.functions import ExtractYear, ExtractMonth
    from datetime import datetime, timedelta
    from django.views.decorators.cache import cache_page
    from django.core.cache import cache
    import json
    
    user = request.user
    
    # Date range filter
    days = int(request.GET.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)
    
    # Check cache first
    cache_key = f"analytics_{user.id}_{days}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'core/analytics.html', cached_data)
    
    # Base bill queryset with all filters
    all_bills = Bill.objects.filter(store_name=user)
    recent_bills_qs = all_bills.filter(date__gte=start_date)
    prev_bills_qs = all_bills.filter(date__gte=start_date - timedelta(days=days*2), date__lt=start_date)
    
    # Aggregate all metrics in single queries where possible
    all_metrics = all_bills.aggregate(
        total_revenue=Sum('total_price'),
        total_bills=Count('id'),
        avg_order_value=Avg('total_price')
    )
    
    recent_metrics = recent_bills_qs.aggregate(
        recent_revenue=Sum('total_price'),
        recent_bills=Count('id')
    )
    
    prev_metrics = prev_bills_qs.aggregate(
        prev_revenue=Sum('total_price'),
        prev_bills=Count('id')
    )
    
    # Growth calculations
    total_revenue = all_metrics['total_revenue'] or 0
    total_bills = all_metrics['total_bills'] or 0
    avg_order_value = all_metrics['avg_order_value'] or 0
    
    recent_revenue = recent_metrics['recent_revenue'] or 0
    recent_bills = recent_metrics['recent_bills'] or 0
    
    prev_revenue = prev_metrics['prev_revenue'] or 1
    prev_bills = prev_metrics['prev_bills'] or 1
    
    revenue_growth = ((recent_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    bills_growth = ((recent_bills - prev_bills) / prev_bills * 100) if prev_bills > 0 else 0
    
    # Use .only() to reduce data transfer for products and clients
    top_products = Product.objects.filter(
        user=user, status=True, product_status='published'
    ).only('title', 'price', 'category_id').order_by('-price')[:5]
    
    # Optimize client query with annotations
    top_clients = Client.objects.filter(user=user).annotate(
        revenue=Sum('bill__total_price'),
        bill_count=Count('bill', distinct=True)
    ).filter(revenue__isnull=False).only(
        'full_name', 'email', 'phone'
    ).order_by('-revenue')[:5]
    
    # Revenue trend - batch all in one query
    bills_for_trend = recent_bills_qs.values('date').annotate(
        total=Sum('total_price')
    ).order_by('date')
    
    revenue_trend = json.dumps([
        {'day': str(item['date']), 'total': float(item['total'] or 0)}
        for item in bills_for_trend
    ])
    
    # Recent transactions with select_related for client
    recent_transactions = all_bills.select_related('client').only(
        'date', 'description', 'total_price', 'client__full_name'
    ).order_by('-date')[:10]
    
    # Count queries separately (these are cheap)
    total_products = Product.objects.filter(user=user).count()
    total_clients = Client.objects.filter(user=user).count()
    
    context = {
        'total_revenue': total_revenue,
        'recent_revenue': recent_revenue,
        'revenue_growth': revenue_growth,
        'total_bills': total_bills,
        'recent_bills': recent_bills,
        'bills_growth': bills_growth,
        'total_products': total_products,
        'total_clients': total_clients,
        'avg_order_value': avg_order_value,
        'top_products': top_products,
        'top_clients': top_clients,
        'revenue_trend': revenue_trend,
        'recent_transactions': recent_transactions,
        'days': days,
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, context, 300)
    return render(request, 'core/analytics.html', context)

@login_required(login_url='/login/')
def clients(request):
    # Remove the filter to see all clients first (for debugging)
    clients = Client.objects.filter(user=request.user).order_by('-id')
    
    # Add debug info
    total_clients = Client.objects.count()
    user_clients = clients.count()
    
    print(f"Total clients in database: {total_clients}")
    print(f"Clients for user {request.user.username}: {user_clients}")
    
    # If no clients found, check if user field exists
    if user_clients == 0 and total_clients > 0:
        print("WARNING: Clients exist but none are associated with current user!")
        # Optionally show all clients for debugging
        clients = Client.objects.all().order_by('-id')

    context = {
        'clients': clients,
        'total_clients': total_clients,
        'user_clients': user_clients,
    }
    return render(request, 'core/clients.html', context)

@login_required(login_url='/login/')
def client_detail(request, lid):
    client = Client.objects.get(lid=lid)
    # Fetch bills related to the client
    bills = Bill.objects.filter(client=client).prefetch_related('items').order_by('-date', '-id')
    
    # Calculate statistics
    total_revenue = bills.aggregate(total=Sum("total_price"))["total"] or 0
    total_quantity = bills.aggregate(total=Sum("quantity"))["total"] or 0
    avg_bill = (total_revenue / bills.count()) if bills.count() > 0 else 0

    context = {
        'client': client,
        'bills': bills,
        'total_revenue': total_revenue,
        'total_quantity': total_quantity,
        'avg_bill': avg_bill,
    }
    return render(request, 'core/client-bills.html', context)

@login_required(login_url='/login/')
def dashboard(request):
    from django.core.cache import cache
    from django.db.models import Sum, Count, Avg, Q
    from datetime import datetime
    import json
    
    logger = logging.getLogger(__name__)
    t_start = time.perf_counter()
    timings = {}
    user = request.user
    
    # Check cache first
    cache_key = f"dashboard_{user.id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'core/dashboard.html', cached_data)
    
    # Filter data for current user
    bills = Bill.objects.filter(store_name=user)
    products = Product.objects.filter(user=user)
    clients = Client.objects.filter(user=user)
    timings["query_load"] = round((time.perf_counter() - t_start) * 1000)
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    
    today_bills = bills.filter(date=today)
    this_month_bills = bills.filter(date__gte=this_month_start)

    # Aggregate all KPIs in fewer queries
    all_metrics = bills.aggregate(
        total_revenue=Sum("total_price"),
        total_quantity=Sum("quantity"),
        bills_count=Count('id')
    )
    
    today_metrics = today_bills.aggregate(
        today_revenue=Sum("total_price"),
        today_bills=Count('id')
    )
    
    month_metrics = this_month_bills.aggregate(
        month_revenue=Sum("total_price"),
        month_bills=Count('id')
    )
    
    # Count queries (these are fast)
    total_clients = clients.count()
    total_products = products.count()
    
    bills_count = all_metrics['bills_count'] or 0
    total_revenue = all_metrics['total_revenue'] or 0
    
    kpis = {
        "total_revenue": total_revenue,
        "total_quantity": all_metrics['total_quantity'] or 0,
        "total_clients": total_clients,
        "total_products": total_products,
        "today_revenue": today_metrics['today_revenue'] or 0,
        "today_bills": today_metrics['today_bills'] or 0,
        "month_revenue": month_metrics['month_revenue'] or 0,
        "month_bills": month_metrics['month_bills'] or 0,
        "avg_bill_value": (total_revenue / bills_count) if bills_count > 0 else 0,
    }
    timings["kpis"] = round((time.perf_counter() - t_start) * 1000)

    # Top clients - convert to JSON for Chart.js
    top_clients_qs = bills.values("client__full_name").annotate(
        revenue=Sum("total_price"),
        qty=Sum("quantity"),
        bills_count=Count('id')
    ).order_by("-revenue")[:8]
    
    top_clients_data = list(top_clients_qs)
    top_clients_chart = json.dumps({
        'labels': [c['client__full_name'] for c in top_clients_data],
        'revenue': [float(c['revenue'] or 0) for c in top_clients_data]
    })
    timings["top_clients_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Top products - convert to JSON for Chart.js
    top_products_qs = bills.values("description").annotate(
        qty=Sum("quantity"),
        revenue=Sum("total_price")
    ).order_by("-qty")[:8]
    
    top_products_data = list(top_products_qs)
    top_products_chart = json.dumps({
        'labels': [p['description'][:30] for p in top_products_data],
        'quantity': [float(p['qty'] or 0) for p in top_products_data]
    })
    timings["top_products_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Monthly revenue trend
    monthly_data = bills.annotate(
        year=ExtractYear('date'),
        month=ExtractMonth('date')
    ).values('year', 'month').annotate(
        total=Sum('total_price')
    ).order_by('year', 'month')
    
    monthly_list = list(monthly_data)
    monthly_chart = json.dumps({
        'labels': [f"{item['year']}-{item['month']:02d}" for item in monthly_list],
        'revenue': [float(item['total'] or 0) for item in monthly_list]
    })
    timings["monthly_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Today's bar chart
    bar_chart = None
    if today_bills.exists():
        today_data = list(today_bills.values('description', 'quantity')[:10])
        bar_chart = json.dumps({
            'labels': [item['description'][:30] for item in today_data],
            'quantity': [float(item['quantity'] or 0) for item in today_data]
        })
    timings["bar_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Recent bills table
    recent = bills.select_related('client').only(
        "description", "quantity", "total_price", "date", "client__full_name"
    ).order_by("-date")[:10]
    table_chart = json.dumps([
        {
            'date': bill.date.strftime('%Y-%m-%d'),
            'client': bill.client.full_name if bill.client else 'Unknown',
            'total': float(bill.total_price or 0),
            'items': int(bill.quantity or 0)
        }
        for bill in recent
    ])
    timings["table_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Pie chart - product share
    pie_data = bills.values("description").annotate(
        qty=Sum("quantity")
    ).order_by("-qty")[:8]
    
    pie_chart = json.dumps({
        'labels': [item['description'][:30] for item in pie_data],
        'values': [float(item['qty'] or 0) for item in pie_data]
    })
    timings["pie_chart"] = round((time.perf_counter() - t_start) * 1000)

    line_chart = monthly_chart

    # Optional geocoding with caching (only when requested)
    geo_data = None
    map_chart = None
    show_geo = request.GET.get("show_geo") == "1"
    if show_geo:
        geo_cache_key = f"geo_data_{user.id}"
        geo_data = cache.get(geo_cache_key)
        if not geo_data:
            geolocator = Nominatim(user_agent="store_performance_dashboard")
            locations = []
            client_list = Client.objects.filter(user=user).only(
                "full_name", "address", "city", "country", "profile_image", "phone", "lid"
            )
            for client in client_list:
                location_parts = [client.address, client.city, client.country]
                location_str = ", ".join([p for p in location_parts if p])
                if not location_str:
                    continue

                client_cache_key = f"geo_client_{client.id}_{hash(location_str)}"
                cached_coords = cache.get(client_cache_key)
                coords = None
                if cached_coords is not None:
                    coords = cached_coords
                else:
                    try:
                        geo = geolocator.geocode(location_str, timeout=1.5)
                        if geo:
                            coords = (geo.latitude, geo.longitude)
                        cache.set(client_cache_key, coords, 86400)  # 1 day
                    except Exception:
                        coords = None

                if not coords:
                    continue

                image_url = client.profile_image.url if client.profile_image else ""
                locations.append({
                    "lid": client.lid,
                    "name": client.full_name or "",
                    "location": location_str,
                    "address": client.address or "",
                    "city": client.city or "",
                    "phone": client.phone or "",
                    "profile_image": image_url,
                    "lat": coords[0],
                    "lon": coords[1],
                })

            if locations:
                geo_data = json.dumps(locations)
                cache.set(geo_cache_key, geo_data, 86400)  # cache for 1 day

    timings["geo_data"] = round((time.perf_counter() - t_start) * 1000)

    # Log timings summary
    logger.info("Dashboard timings (ms): %s", timings)

    context = {
        "kpis": kpis,
        "bar_chart": bar_chart,
        "table_chart": table_chart,
        "pie_chart": pie_chart,
        "line_chart": line_chart,
        "map_chart": map_chart,
        "top_clients_chart": top_clients_chart,
        "top_products_chart": top_products_chart,
        "geo_data": geo_data,
        "show_geo": show_geo,
        "debug": request.GET.get("debug") == "1",
        "timings": timings,
    }
    
    # Cache for 3 minutes
    cache.set(cache_key, context, 180)
    return render(request, 'core/dashboard.html', context)

@login_required(login_url='/login/')
def products(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if a new category name is provided
            new_category_name = request.POST.get('new_category', None)
            product = form.save(commit=False)  # Save the form temporarily without committing to the database
            product.user = request.user  # Assign the current user to the product's user field

            if new_category_name:
                # Create a new category or get the existing one with the provided name
                category, created = Category.objects.get_or_create(title=new_category_name)
                product.category = category  # Assign the new or existing category to the product

            product.save()  # Now save the product to the database
            return redirect("core:products")  # Redirect to a new URL
    else:
        form = ProductForm()

    products = Product.objects.filter(user=request.user).order_by('-date')
    # Fetch distinct categories
    categories = Category.objects.all()
    # Fetch all clients for the current user
    clients = Client.objects.filter(user=request.user).order_by('full_name')

    context = {
        'products': products,
        'categories': categories,
        'clients': clients,
        'form': form,
    }

    return render(request, 'core/products.html', context)

@login_required(login_url='/login/')
@transaction.atomic
def create_bill(request):
    # For GET requests, render the multi-bill creation page
    if request.method == 'GET':
        # Get all existing clients for the dropdown
        clients = Client.objects.filter(user=request.user).order_by('-id')[:50]
        return render(request, 'core/create-bill.html', {
            'user': request.user,
            'clients': clients,
        })

    # POST: Handle bill creation
    if request.method == 'POST':
        client_name = request.POST.get('clientName', '').strip()
        bill_date = request.POST.get('billDate')
        
        # Validate client name is not empty
        if not client_name:
            messages.error(request, 'Client name is required.')
            return render(request, 'core/create-bill.html', {'user': request.user})

        # Parse bill items sent as JSON
        items_json = request.POST.get('items_json', '')
        try:
            items_data = json.loads(items_json) if items_json else []
        except json.JSONDecodeError:
            messages.error(request, 'Invalid items payload. Please try again.')
            return render(request, 'core/create-bill.html', {'user': request.user})

        if not items_data:
            messages.error(request, 'Please add at least one product to the bill.')
            return render(request, 'core/create-bill.html', {'user': request.user})

        try:
            # Resolve or create client - now with more fields from multi-bill form
            client_select = request.POST.get('clientSelect')
            if client_select:
                client = Client.objects.get(lid=client_select, user=request.user)
                created = False
            else:
                # Check if client exists by name first
                existing_client = Client.objects.filter(
                    full_name=client_name,
                    user=request.user
                ).first()
                
                if existing_client:
                    # Update existing client with new info if provided
                    client = existing_client
                    created = False
                    
                    # Update fields if provided
                    if request.POST.get('phone'):
                        client.phone = request.POST.get('phone', '')
                    if request.POST.get('email'):
                        client.email = request.POST.get('email', '')
                    if request.POST.get('address'):
                        client.address = request.POST.get('address', '')
                    
                    client.save()
                else:
                    # Create new client
                    client = Client.objects.create(
                        full_name=client_name,
                        user=request.user,
                        address=request.POST.get('address', ''),
                        phone=request.POST.get('phone', ''),
                        email=request.POST.get('email', ''),
                        city=request.POST.get('city', ''),
                        country=request.POST.get('country', ''),
                        postal_code=request.POST.get('postal_code', ''),
                    )
                    created = True

            parsed_items = []
            total_price = Decimal('0')
            total_qty = Decimal('0')

            for item in items_data:
                title = (item.get('title') or item.get('description') or '').strip()
                price = Decimal(str(item.get('price', 0)))
                qty = Decimal(str(item.get('quantity', 0)))
                amount = price * qty
                total_price += amount
                total_qty += qty
                parsed_items.append({
                    'description': title,
                    'price': price,
                    'quantity': qty,
                    'amount': amount,
                })

            # Build a summary description for quick views/search
            description_summary = ", ".join([p['description'] for p in parsed_items if p['description']])

            bill = Bill.objects.create(
                store_name=request.user,
                client=client,
                date=bill_date if bill_date else timezone.now().date(),
                quantity=total_qty,
                description=description_summary[:255],
                price=parsed_items[0]['price'] if parsed_items else Decimal('0'),
                amount=total_price,
                total_price=total_price,
            )

            BillItem.objects.bulk_create([
                BillItem(
                    bill=bill,
                    description=item['description'],
                    quantity=item['quantity'],
                    price=item['price'],
                    amount=item['amount'],
                ) for item in parsed_items
            ])

            # Success message
            if created:
                messages.success(request, f'New client "{client_name}" created and bill saved successfully!')
            else:
                messages.success(request, f'Bill saved successfully for client "{client_name}"!')

            # Return success response for AJAX
            # If it's an AJAX request, return JSON; otherwise redirect
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True,
                    'message': 'Bill saved successfully!',
                    'client_id': str(client.lid)
                })
            else:
                return redirect('core:client_detail', lid=client.lid)
            
        except Client.DoesNotExist:
            from django.http import JsonResponse
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Selected client not found.'}, status=400)
            messages.error(request, 'Selected client not found.')
            return render(request, 'core/create-bill.html', {'user': request.user})
        except (ValueError, InvalidOperation) as ve:
            from django.http import JsonResponse
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'Invalid number format: {str(ve)}'}, status=400)
            messages.error(request, f'Invalid number format: {str(ve)}')
            return render(request, 'core/create-bill.html', {'user': request.user})
        except Exception as e:
            from django.http import JsonResponse
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'Error creating bill: {str(e)}'}, status=500)
            messages.error(request, f'Error creating bill: {str(e)}')
            return render(request, 'core/create-bill.html', {'user': request.user})

@login_required(login_url='/login/')
def reports(request):
    from django.db.models import Sum, Count, Avg, F, Q
    from django.db.models.functions import ExtractYear, ExtractMonth
    from datetime import datetime, timedelta
    from django.core.cache import cache
    import json
    
    user = request.user
    
    # Report type filter
    report_type = request.GET.get('type', 'summary')
    period = request.GET.get('period', 'monthly')
    
    # Date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
    
    # Check cache
    cache_key = f"reports_{user.id}_{report_type}_{period}_{start_date.date()}_{end_date.date()}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'core/reports.html', cached_data)
    
    # Base queryset - filtered once, reused multiple times
    bills = Bill.objects.filter(store_name=user, date__gte=start_date, date__lte=end_date)
    
    # Aggregate all summary stats in single query
    summary_metrics = bills.aggregate(
        total_revenue=Sum('total_price'),
        total_transactions=Count('id'),
        avg_transaction=Avg('total_price'),
        total_quantity=Sum('quantity'),
        unique_clients=Count('client', distinct=True)
    )
    
    summary_data = {
        'total_revenue': summary_metrics['total_revenue'] or 0,
        'total_transactions': summary_metrics['total_transactions'] or 0,
        'avg_transaction': summary_metrics['avg_transaction'] or 0,
        'total_quantity': summary_metrics['total_quantity'] or 0,
        'unique_clients': summary_metrics['unique_clients'] or 0,
    }
    
    # Revenue by period - optimized
    if period == 'monthly':
        monthly_data = bills.annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        ).values('year', 'month').annotate(
            revenue=Sum('total_price'),
            transactions=Count('id', distinct=True)
        ).order_by('year', 'month')
        
        revenue_by_period = json.dumps([
            {
                'period': f"{item['year']}-{item['month']:02d}-01",
                'revenue': float(item['revenue'] or 0),
                'transactions': item['transactions']
            }
            for item in monthly_data
        ])
    else:
        daily_data = bills.values('date').annotate(
            revenue=Sum('total_price'),
            transactions=Count('id', distinct=True)
        ).order_by('date')
        
        revenue_by_period = json.dumps([
            {
                'period': str(item['date']),
                'revenue': float(item['revenue'] or 0),
                'transactions': item['transactions']
            }
            for item in daily_data
        ])
    
    # Product performance - use only() to reduce data
    product_performance = Product.objects.filter(
        user=user, status=True, product_status='published'
    ).only('title', 'price', 'stock', 'product_status', 'category_id').order_by('-price')[:10]
    
    # Client analysis - optimized with only()
    client_analysis = Client.objects.filter(user=user).annotate(
        total_spent=Sum('bill__total_price'),
        visit_count=Count('bill', distinct=True),
        avg_purchase=Avg('bill__total_price')
    ).only('full_name', 'email', 'phone').order_by('-total_spent')[:10]
    
    # Category breakdown - optimized
    category_breakdown = Category.objects.filter(
        product__user=user
    ).annotate(
        product_count=Count('product', distinct=True),
        avg_price=Avg('product__price')
    ).filter(product_count__gt=0).order_by('-product_count').distinct()
    
    context = {
        'report_type': report_type,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'summary_data': summary_data,
        'revenue_by_period': revenue_by_period,
        'product_performance': product_performance,
        'client_analysis': client_analysis,
        'category_breakdown': category_breakdown,
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, context, 300)
    return render(request, 'core/reports.html', context)
    
    context = {
        'report_type': report_type,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'summary_data': summary_data,
        'revenue_by_period': revenue_by_period,
        'product_performance': product_performance,
        'client_analysis': client_analysis,
        'category_breakdown': category_breakdown,
    }
    return render(request, 'core/reports.html', context)

@login_required(login_url='/login/')
def settings(request):
    # Get user data and statistics
    user = request.user
    user_products = Product.objects.filter(user=user).count()
    user_clients = Client.objects.filter(user=user).count()
    user_bills = Bill.objects.filter(store_name=user).count()
    total_revenue = Bill.objects.filter(store_name=user).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    context = {
        'user': user,
        'user_products': user_products,
        'user_clients': user_clients,
        'user_bills': user_bills,
        'total_revenue': total_revenue,
        'profile_image': user.image.url if user.image else None,
        'is_admin': user.is_staff or user.is_superuser,
    }
    return render(request, 'core/settings.html', context)

@login_required(login_url='/login/')
def profile(request):
    """View and edit user profile information"""
    user = request.user
    is_admin = user.is_staff or user.is_superuser
    
    if request.method == 'POST':
        try:
            # Update user fields
            user.username = request.POST.get('username', user.username)
            user.email = request.POST.get('email', user.email)
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.phone = request.POST.get('phone', '')
            user.bio = request.POST.get('bio', '')
            
            # Handle profile image upload
            if 'image' in request.FILES:
                user.image = request.FILES['image']
            
            user.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('core:profile')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'user': user,
        'profile_image': user.image.url if user.image else None,
        'is_admin': is_admin,
    }
    return render(request, 'core/profile.html', context)


# Bill Actions
@login_required(login_url='/login/')
def edit_bill(request, bill_id):
    """Edit bill details"""
    try:
        bill = Bill.objects.get(id=bill_id)
        
        if request.method == 'POST':
            # Update bill fields
            bill.description = request.POST.get('description', bill.description)
            bill.quantity = Decimal(str(request.POST.get('quantity', bill.quantity)))
            bill.price = Decimal(str(request.POST.get('price', bill.price)))
            bill.amount = Decimal(str(request.POST.get('amount', bill.amount)))
            bill.total_price = Decimal(str(request.POST.get('total_price', bill.total_price)))
            
            bill.save()

            # Update the first bill item to stay in sync (basic edit support)
            first_item = bill.items.first()
            if first_item:
                first_item.description = bill.description
                first_item.quantity = bill.quantity
                first_item.price = bill.price
                first_item.amount = bill.amount
                first_item.save()
            messages.success(request, 'Bill updated successfully!')
            
            # Redirect back to client bills page
            return redirect('core:client_detail', lid=bill.client.lid)
        
        messages.error(request, 'Invalid request method')
        return redirect('core:client_detail', lid=bill.client.lid)
        
    except Bill.DoesNotExist:
        messages.error(request, 'Bill not found')
        return redirect('core:clients')
    except Exception as e:
        messages.error(request, f'Error updating bill: {str(e)}')
        return redirect('core:clients')


@login_required(login_url='/login/')
def delete_bill(request, bill_id):
    """Delete a bill"""
    try:
        bill = Bill.objects.get(id=bill_id)
        client_lid = bill.client.lid
        
        if request.method == 'POST':
            bill.delete()
            messages.success(request, 'Bill deleted successfully!')
            return redirect('core:client_detail', lid=client_lid)
        
        messages.error(request, 'Invalid request method')
        return redirect('core:client_detail', lid=client_lid)
        
    except Bill.DoesNotExist:
        messages.error(request, 'Bill not found')
        return redirect('core:clients')
    except Exception as e:
        messages.error(request, f'Error deleting bill: {str(e)}')
        return redirect('core:clients')


@login_required(login_url='/login/')
def print_bill(request, bill_id):
    """Print/view bill in a printable format"""
    try:
        bill = Bill.objects.get(id=bill_id)
        context = {
            'bill': bill,
            'client': bill.client,
        }
        return render(request, 'core/print-bill.html', context)
    except Bill.DoesNotExist:
        messages.error(request, 'Bill not found')
        return redirect('core:clients')
    except Exception as e:
        messages.error(request, f'Error printing bill: {str(e)}')
        return redirect('core:clients')


@login_required(login_url='/login/')
def duplicate_bill(request, bill_id):
    """Duplicate a bill"""
    try:
        original_bill = Bill.objects.get(id=bill_id)
        client_lid = original_bill.client.lid
        
        # Create a new bill with the same details but new ID
        new_bill = Bill.objects.create(
            client=original_bill.client,
            store_name=original_bill.store_name,
            description=original_bill.description,
            quantity=original_bill.quantity,
            price=original_bill.price,
            amount=original_bill.amount,
            total_price=original_bill.total_price,
            date=timezone.now().date(),
        )
        # Copy bill items
        if hasattr(original_bill, 'items'):
            BillItem.objects.bulk_create([
                BillItem(
                    bill=new_bill,
                    description=item.description,
                    quantity=item.quantity,
                    price=item.price,
                    amount=item.amount,
                ) for item in original_bill.items.all()
            ])
        
        messages.success(request, f'Bill #{new_bill.id} created successfully!')
        return redirect('core:client_detail', lid=client_lid)
        
    except Bill.DoesNotExist:
        messages.error(request, 'Original bill not found')
        return redirect('core:clients')
    except Exception as e:
        messages.error(request, f'Error duplicating bill: {str(e)}')
        return redirect('core:clients')


@login_required(login_url='/login/')
def get_bill_data(request, bill_id):
    """API endpoint to get bill data for editing"""
    try:
        from django.http import JsonResponse
        
        bill = Bill.objects.get(id=bill_id)
        
        # Get bill items or create from legacy data
        items = []
        if bill.items.exists():
            items = [
                {
                    'id': item.id,
                    'description': item.description,
                    'quantity': float(item.quantity),
                    'price': float(item.price),
                    'amount': float(item.amount)
                }
                for item in bill.items.all()
            ]
        elif bill.description:
            # Legacy bill - convert to item format
            items = [{
                'id': None,
                'description': bill.description,
                'quantity': float(bill.quantity),
                'price': float(bill.price),
                'amount': float(bill.amount)
            }]
        
        data = {
            'id': bill.id,
            'client_name': bill.client.full_name if bill.client else 'Unknown',
            'client_id': bill.client.lid if bill.client else None,
            'date': bill.date.strftime('%b %d, %Y'),
            'items': items,
            'total': float(bill.total_price)
        }
        
        return JsonResponse(data)
        
    except Bill.DoesNotExist:
        return JsonResponse({'error': 'Bill not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/login/')
def update_bill_items(request, bill_id):
    """API endpoint to update bill items"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        from django.http import JsonResponse
        
        bill = Bill.objects.get(id=bill_id)
        data = json.loads(request.body)
        items_data = data.get('items', [])
        
        if not items_data:
            return JsonResponse({'error': 'No items provided'}, status=400)
        
        # Delete existing items
        bill.items.all().delete()
        
        # Create new items
        total_price = Decimal('0')
        total_qty = Decimal('0')
        descriptions = []
        
        for item_data in items_data:
            desc = item_data.get('description', '').strip()
            qty = Decimal(str(item_data.get('quantity', 0)))
            price = Decimal(str(item_data.get('price', 0)))
            amount = qty * price
            
            BillItem.objects.create(
                bill=bill,
                description=desc,
                quantity=qty,
                price=price,
                amount=amount
            )
            
            total_price += amount
            total_qty += qty
            descriptions.append(desc)
        
        # Update bill summary
        bill.description = ', '.join(descriptions)[:255]
        bill.quantity = total_qty
        bill.price = Decimal(str(items_data[0].get('price', 0))) if items_data else Decimal('0')
        bill.amount = total_price
        bill.total_price = total_price
        bill.save()
        
        messages.success(request, 'Bill updated successfully!')
        return JsonResponse({'success': True})
        
    except Bill.DoesNotExist:
        return JsonResponse({'error': 'Bill not found'}, status=404)
    except (ValueError, InvalidOperation) as e:
        return JsonResponse({'error': f'Invalid number format: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/login/')
def products_api(request):
    """API endpoint to get products for bill editor"""
    try:
        from django.http import JsonResponse
        
        products = Product.objects.filter(user=request.user).order_by('-date')[:100]
        
        products_data = [
            {
                'id': p.id,
                'title': p.title,
                'price': float(p.price),
                'image': p.image.url if p.image else '/static/images/product-placeholder.png',
                'category': p.category.title if p.category else 'Uncategorized'
            }
            for p in products
        ]
        
        return JsonResponse({'products': products_data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='/login/')
def update_client_picture(request):
    """Update client's profile picture"""
    if request.method == 'POST':
        client_lid = request.POST.get('client_lid')
        
        try:
            client = Client.objects.get(lid=client_lid, user=request.user)
            
            if 'profile_image' in request.FILES:
                client.profile_image = request.FILES['profile_image']
                client.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Picture updated successfully',
                    'image_url': client.profile_image.url if client.profile_image else ''
                })
            else:
                return JsonResponse({'success': False, 'error': 'No image file provided'}, status=400)
                
        except Client.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Client not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
