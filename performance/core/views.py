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
import time
import logging

@login_required(login_url='/login/')
def analytics(request):
    from django.db.models import Sum, Count, Avg, F, Q
    from django.db.models.functions import TruncDate, TruncMonth
    from datetime import datetime, timedelta
    import json
    
    user = request.user
    
    # Date range filter
    days = int(request.GET.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)
    
    # Overall metrics
    total_revenue = Bill.objects.filter(store_name=user).aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_bills = Bill.objects.filter(store_name=user).count()
    total_products = Product.objects.filter(user=user).count()
    total_clients = Client.objects.filter(user=user).count()
    
    # Recent period metrics
    recent_revenue = Bill.objects.filter(store_name=user, date__gte=start_date).aggregate(Sum('total_price'))['total_price__sum'] or 0
    recent_bills = Bill.objects.filter(store_name=user, date__gte=start_date).count()
    
    # Previous period for comparison
    prev_start = start_date - timedelta(days=days)
    prev_revenue = Bill.objects.filter(store_name=user, date__gte=prev_start, date__lt=start_date).aggregate(Sum('total_price'))['total_price__sum'] or 1
    prev_bills = Bill.objects.filter(store_name=user, date__gte=prev_start, date__lt=start_date).count() or 1
    
    # Growth calculations
    revenue_growth = ((recent_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    bills_growth = ((recent_bills - prev_bills) / prev_bills * 100) if prev_bills > 0 else 0
    
    # Top products by price (since bills don't reference products directly)
    top_products = Product.objects.filter(user=user, status=True, product_status='published').order_by('-price')[:5]
    
    # Top clients by revenue
    top_clients = Client.objects.filter(user=user).annotate(
        revenue=Sum('bill__total_price'),
        bill_count=Count('bill')
    ).filter(revenue__isnull=False).order_by('-revenue')[:5]
    
    # Revenue trend (daily)
    revenue_trend_raw = Bill.objects.filter(
        store_name=user, 
        date__gte=start_date
    ).annotate(day=TruncDate('date')).values('day').annotate(
        total=Sum('total_price')
    ).order_by('day')
    
    # Convert to JSON-serializable format
    revenue_trend = json.dumps([
        {'day': item['day'].isoformat(), 'total': float(item['total'] or 0)}
        for item in revenue_trend_raw
    ])
    
    # Recent transactions
    recent_transactions = Bill.objects.filter(store_name=user).select_related('client').order_by('-date')[:10]
    
    # Average order value
    avg_order_value = Bill.objects.filter(store_name=user).aggregate(Avg('total_price'))['total_price__avg'] or 0
    
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
    logger = logging.getLogger(__name__)
    t_start = time.perf_counter()
    timings = {}
    # Filter data for current user
    bills = Bill.objects.filter(store_name=request.user).select_related('client')
    products = Product.objects.filter(user=request.user)
    clients = Client.objects.filter(user=request.user)
    timings["query_load"] = round((time.perf_counter() - t_start) * 1000)
    
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    
    today_bills = bills.filter(date=today)
    this_month_bills = bills.filter(date__gte=this_month_start)

    # KPIs - Overall
    total_revenue = bills.aggregate(total=Sum("total_price"))["total"] or 0
    total_quantity = bills.aggregate(total=Sum("quantity"))["total"] or 0
    
    # KPIs - Today
    today_revenue = today_bills.aggregate(total=Sum("total_price"))["total"] or 0
    today_bills_count = today_bills.count()
    
    # KPIs - This Month
    month_revenue = this_month_bills.aggregate(total=Sum("total_price"))["total"] or 0
    month_bills_count = this_month_bills.count()
    
    bills_count = bills.count()
    kpis = {
        "total_revenue": total_revenue,
        "total_quantity": total_quantity,
        "total_clients": clients.count(),
        "total_products": products.count(),
        "today_revenue": today_revenue,
        "today_bills": today_bills_count,
        "month_revenue": month_revenue,
        "month_bills": month_bills_count,
        "avg_bill_value": (total_revenue / bills_count) if bills_count > 0 else 0,
    }
    timings["kpis"] = round((time.perf_counter() - t_start) * 1000)

    # Top clients (by revenue)
    top_clients_qs = (
        bills.values("client__full_name")
        .annotate(revenue=Sum("total_price"), qty=Sum("quantity"), bills_count=Count('id'))
        .order_by("-revenue")[:8]
    )
    top_clients_df = pd.DataFrame(list(top_clients_qs))
    top_clients_chart = None
    if not top_clients_df.empty:
        top_clients_chart = px.bar(
            top_clients_df,
            x="client__full_name",
            y="revenue",
            color="qty",
            title="Top Clients by Revenue",
            labels={"client__full_name": "Client", "revenue": "Revenue ($)", "qty": "Units Sold"},
        ).to_html(full_html=False, include_plotlyjs=False)
    timings["top_clients_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Top products (by quantity)
    top_products_qs = (
        bills.values("description")
        .annotate(qty=Sum("quantity"), revenue=Sum("total_price"), avg_price=Avg('price'))
        .order_by("-qty")[:8]
    )
    top_products_df = pd.DataFrame(list(top_products_qs))
    top_products_chart = None
    if not top_products_df.empty:
        top_products_chart = px.bar(
            top_products_df,
            x="description",
            y="qty",
            color="revenue",
            title="Top Products by Quantity",
            labels={"description": "Product", "qty": "Quantity Sold", "revenue": "Revenue ($)"},
        ).to_html(full_html=False, include_plotlyjs=False)
    timings["top_products_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Monthly revenue trend
    monthly_chart = None
    monthly_df = pd.DataFrame(list(bills.values("date", "total_price")))
    if not monthly_df.empty:
        monthly_df["month"] = pd.to_datetime(monthly_df["date"]).dt.to_period("M").dt.to_timestamp()
        grouped = monthly_df.groupby("month")["total_price"].sum().reset_index()
        monthly_chart = px.line(
            grouped,
            x="month",
            y="total_price",
            markers=True,
            title="Monthly Revenue Trend",
            labels={"month": "Month", "total_price": "Revenue"},
        ).to_html(full_html=False, include_plotlyjs=False)
    timings["monthly_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Today's bar chart (kept)
    bar_chart = None
    if today_bills.exists():
        product_descriptions = [bill.description for bill in today_bills]
        quantities_sold = [bill.quantity for bill in today_bills]
        fig = px.bar(x=product_descriptions, y=quantities_sold, title="Today's Sold Products")
        fig.update_layout(xaxis_title="Products", yaxis_title="Quantities")
        bar_chart = fig.to_html(full_html=False, include_plotlyjs=False)
    timings["bar_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Table (recent bills)
    table_chart = None
    recent = bills.only("description", "quantity", "total_price", "date", "client").order_by("-date")[:10]
    if recent.exists():
        table_data = [["Client", "Product", "Qty", "Total Price", "Date"]]
        for b in recent:
            table_data.append([str(b.client), b.description, b.quantity, b.total_price, b.date])
        table_chart = ff.create_table(table_data, height_constant=40).to_html(full_html=False, include_plotlyjs=False)
    timings["table_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Pie: product share
    pie_chart = None
    pie_df = pd.DataFrame(list(bills.values("description").annotate(qty=Sum("quantity"))))
    if not pie_df.empty:
        pie_chart = px.pie(
            pie_df,
            values="qty",
            names="description",
            title="Product Share",
        ).to_html(full_html=False, include_plotlyjs=False)
    timings["pie_chart"] = round((time.perf_counter() - t_start) * 1000)

    # Line: monthly high/low simplified to trend already covered; keep original line as fallback
    line_chart = monthly_chart

    # Optional dynamic map showing all client locations (cities/addresses)
    geo_data = None
    show_geo = request.GET.get("show_geo") == "1"
    if show_geo and clients.exists():
        # Fetch all clients with their address/city/image; prepare JSON for Leaflet map
        client_list = clients  # Use queryset directly to access image URL method
        if client_list:
            # Geocode each client location and build location entries
            geolocator = Nominatim(user_agent="store_performance")
            locations = []
            
            for client in client_list:
                # Use address if available, otherwise use city
                location_str = client.address or client.city or "Unknown"
                lat, lon = None, None
                
                # Try to geocode the location
                try:
                    if location_str != "Unknown":
                        geo = geolocator.geocode(location_str, timeout=3)
                        if geo:
                            lat, lon = geo.latitude, geo.longitude
                except (GeocoderInsufficientPrivileges, Exception):
                    # If geocoding fails, skip or use default Morocco center
                    lat, lon = 33.5731, -7.5898
                
                # Only add if we have coordinates
                if lat and lon:
                    # Get the full image URL
                    image_url = client.profile_image.url if client.profile_image else "/media/client.png"
                    
                    locations.append({
                        "lid": client.lid,
                        "name": client.full_name or "",
                        "location": location_str,
                        "address": client.address or "",
                        "city": client.city or "",
                        "phone": client.phone or "",
                        "profile_image": image_url,
                        "lat": lat,
                        "lon": lon,
                    })
            
            if locations:
                geo_data = json.dumps(locations)
    timings["geo_data"] = round((time.perf_counter() - t_start) * 1000)

    # Heavy map rendering disabled
    map_chart = None

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
    # Always push users to the inline bill builder on the products page
    products_url = f"{reverse('core:products')}#bill-builder"

    if request.method == 'POST':
        client_name = request.POST.get('clientName', '').strip()
        bill_date = request.POST.get('billDate')
        
        # Validate client name is not empty
        if not client_name:
            messages.error(request, 'Client name is required.')
            return redirect(products_url)

        # Parse bill items sent as JSON
        items_json = request.POST.get('items_json', '')
        try:
            items_data = json.loads(items_json) if items_json else []
        except json.JSONDecodeError:
            messages.error(request, 'Invalid items payload. Please try again.')
            return redirect(products_url)

        if not items_data:
            messages.error(request, 'Please add at least one product to the bill.')
            return redirect(products_url)

        try:
            # Resolve or create client
            client_select = request.POST.get('clientSelect')
            if client_select:
                client = Client.objects.get(lid=client_select, user=request.user)
                created = False
            else:
                client, created = Client.objects.get_or_create(
                    full_name=client_name,
                    user=request.user,
                    defaults={
                        'address': request.POST.get('address', ''),
                        'phone': request.POST.get('phone', ''),
                        'email': request.POST.get('email', ''),
                        'city': request.POST.get('city', ''),
                        'country': request.POST.get('country', ''),
                        'postal_code': request.POST.get('postal_code', ''),
                    }
                )

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
                messages.success(request, f'Bill saved successfully for existing client "{client_name}"!')

            return redirect('core:client_detail', lid=client.lid)
            
        except Client.DoesNotExist:
            messages.error(request, 'Selected client not found.')
            return redirect(products_url)
        except (ValueError, InvalidOperation) as ve:
            messages.error(request, f'Invalid number format: {str(ve)}')
            return redirect(products_url)
        except Exception as e:
            messages.error(request, f'Error creating bill: {str(e)}')
            return redirect(products_url)

    # GET requests are redirected to the products page bill builder
    return redirect(products_url)

@login_required(login_url='/login/')
def reports(request):
    from django.db.models import Sum, Count, Avg, F, Q
    from django.db.models.functions import TruncMonth, TruncWeek
    from datetime import datetime, timedelta
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
    
    # Base queryset
    bills = Bill.objects.filter(store_name=user, date__gte=start_date, date__lte=end_date)
    
    # Summary Report
    summary_data = {
        'total_revenue': bills.aggregate(Sum('total_price'))['total_price__sum'] or 0,
        'total_transactions': bills.count(),
        'avg_transaction': bills.aggregate(Avg('total_price'))['total_price__avg'] or 0,
        'total_quantity': bills.aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'unique_clients': bills.values('client').distinct().count(),
    }
    
    # Revenue by period
    if period == 'monthly':
        revenue_by_period_raw = bills.annotate(
            period=TruncMonth('date')
        ).values('period').annotate(
            revenue=Sum('total_price'),
            transactions=Count('id')
        ).order_by('period')
    else:
        revenue_by_period_raw = bills.annotate(
            period=TruncWeek('date')
        ).values('period').annotate(
            revenue=Sum('total_price'),
            transactions=Count('id')
        ).order_by('period')
    
    # Convert to JSON-serializable format
    revenue_by_period = json.dumps([
        {
            'period': item['period'].isoformat() if item['period'] else None,
            'revenue': float(item['revenue'] or 0),
            'transactions': item['transactions']
        }
        for item in revenue_by_period_raw
    ])
    
    # Product performance (by stock/price since bills don't reference products)
    product_performance = Product.objects.filter(user=user, status=True, product_status='published').annotate(
        total_sold=Count('id')  # Placeholder, shows 1 for each product
    ).order_by('-price')[:10]
    
    # Client analysis
    client_analysis = Client.objects.filter(user=user).annotate(
        total_spent=Sum('bill__total_price'),
        visit_count=Count('bill'),
        avg_purchase=Avg('bill__total_price')
    ).order_by('-total_spent')[:10]
    
    # Category breakdown (by product count since no bill-product relationship)
    category_breakdown = Category.objects.filter(user=user).annotate(
        product_count=Count('product'),
        avg_price=Avg('product__price')
    ).filter(product_count__gt=0).order_by('-product_count')
    
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
