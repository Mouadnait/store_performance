import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import timedelta
import pandas as pd
from core.models import (
    Bill, BillItem, Product, Client, Category, Tags, 
    ProductReview, Store, ProductImages
)
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from .forms import ProductForm, ClientForm
from django.utils import timezone
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderInsufficientPrivileges
from django.db import transaction
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Max, Value, IntegerField, DecimalField
from django.db.models.functions import ExtractYear, ExtractMonth, Coalesce
import time
import logging


logger = logging.getLogger(__name__)


def format_decimal_value(value, quantize_pattern='0.01'):
    """Return a string representation of a Decimal value quantized to two places."""
    if value is None:
        decimal_value = Decimal('0')
    elif isinstance(value, Decimal):
        decimal_value = value
    else:
        decimal_value = Decimal(str(value))
    quantize_decimal = Decimal(quantize_pattern)
    return format(decimal_value.quantize(quantize_decimal, rounding=ROUND_HALF_UP), 'f')


def parse_truthy(value, default=False):
    """Parse truthy string flags from request data."""
    if value is None:
        return default
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


def get_current_store(request):
    """Resolve the active store for the current user, preferring ?store= then session, then first store."""
    # Staff can view all stores; regular users see only their own stores.
    store_qs = Store.objects.all() if (request.user.is_staff or request.user.is_superuser) else Store.objects.filter(owner=request.user)
    store_key = request.GET.get('store') or request.session.get('current_store_key')
    store = None

    if store_key:
        # Support both numeric IDs and slugs as selectors
        if str(store_key).isdigit():
            store = store_qs.filter(id=store_key).first()
        else:
            store = store_qs.filter(slug=store_key).first()

    if store is None:
        store = store_qs.order_by('id').first()

    if store:
        # Persist a stable key (slug preferred) in the session
        request.session['current_store_key'] = store.slug or str(store.id)

    return store, store_qs

@login_required(login_url='/login/')
def analytics(request):
    from django.db.models import Sum, Count, Avg, F, Q
    from django.http import JsonResponse
    from django.db.models.functions import ExtractYear, ExtractMonth
    from datetime import datetime, timedelta
    from django.views.decorators.cache import cache_page
    from django.core.cache import cache
    import json
    
    user = request.user
    
    # Resolve store context
    store, store_qs = get_current_store(request)

    # Date range filter
    days = int(request.GET.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)
    from datetime import timedelta
    from django.db.models import Max
    
    # Check cache first
    cache_key = f"analytics_{user.id}_{store.id if store else 'all'}_{days}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'core/statistics/analytics.html', cached_data)
    
    # Base bill queryset with all filters
    all_bills = Bill.objects.filter(store_name=user)
    if store:
        all_bills = all_bills.filter(store=store)
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
    ).only('title', 'price', 'category_id').order_by('-price')
    if store:
        top_products = top_products.filter(store=store)
    top_products = top_products[:5]
    
    # Optimize client query with annotations
    top_clients = Client.objects.filter(user=user).annotate(
        revenue=Sum('bill__total_price'),
        bill_count=Count('bill', distinct=True)
    ).filter(revenue__isnull=False).only(
        'full_name', 'email', 'phone'
    ).order_by('-revenue')
    if store:
        top_clients = top_clients.filter(store=store)
    top_clients = top_clients[:5]
    
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
    product_qs = Product.objects.filter(user=user)
    client_qs = Client.objects.filter(user=user)
    if store:
        product_qs = product_qs.filter(store=store)
        client_qs = client_qs.filter(store=store)
    total_products = product_qs.count()
    total_clients = client_qs.count()
    
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
        'current_store': store,
        'stores': store_qs,
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, context, 300)
    return render(request, 'core/statistics/analytics.html', context)

@login_required(login_url='/login/')
def clients(request):
    """Client portfolio overview for the authenticated merchant."""
    store, store_qs = get_current_store(request)

    client_base = Client.objects.filter(user=request.user)
    if store:
        client_base = client_base.filter(store=store)

    annotated_clients = client_base.annotate(
        bill_count=Count('bill', distinct=True),
        total_spend=Sum('bill__total_price'),
        last_bill_date=Max('bill__date')
    ).order_by('-total_spend', '-bill_count', 'full_name')

    client_records = []
    total_revenue = Decimal('0')
    high_value_threshold = Decimal('1000')
    high_value_clients = 0

    for client in annotated_clients:
        spend = client.total_spend or Decimal('0')
        total_revenue += spend
        if spend >= high_value_threshold:
            high_value_clients += 1
        client_records.append(client)

    total_clients = len(client_records)
    active_clients = sum(1 for client in client_records if client.bill_count)
    inactive_clients = total_clients - active_clients
    repeat_buyers = sum(1 for client in client_records if client.bill_count and client.bill_count >= 3)
    average_revenue = (total_revenue / total_clients) if total_clients else Decimal('0')

    recent_activity = sorted(
        [client for client in client_records if client.last_bill_date],
        key=lambda item: item.last_bill_date,
        reverse=True
    )[:5]

    context = {
        'clients': client_records,
        'overview': {
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': inactive_clients,
            'high_value_clients': high_value_clients,
            'repeat_buyers': repeat_buyers,
            'average_revenue': average_revenue,
            'total_revenue': total_revenue,
        },
        'segments': [
            {'label': 'Active', 'count': active_clients},
            {'label': 'Inactive', 'count': max(inactive_clients, 0)},
            {'label': 'High Value', 'count': high_value_clients},
            {'label': 'Repeat Buyers', 'count': repeat_buyers},
        ],
        'recent_activity': recent_activity,
        'highlight_clients': client_records[:5],
        'client_form': ClientForm(),
        'high_value_threshold': high_value_threshold,
        'current_store': store,
        'stores': store_qs,
    }
    return render(request, 'core/clients/clients.html', context)

@login_required(login_url='/login/')
def client_detail(request, lid):
    """Fetch client bills with ownership verification."""
    store, store_qs = get_current_store(request)

    client_filters = {'lid': lid, 'user': request.user}
    if store:
        client_filters['store'] = store
    client = get_object_or_404(Client, **client_filters)

    bills = Bill.objects.filter(client=client).prefetch_related('items').order_by('-date', '-id')
    bill_count = bills.count()

    aggregates = bills.aggregate(
        total_revenue=Sum('total_price'),
        total_quantity=Sum('quantity'),
        average_ticket=Avg('total_price')
    )

    total_revenue = aggregates['total_revenue'] or Decimal('0')
    total_quantity = aggregates['total_quantity'] or Decimal('0')
    avg_bill = aggregates['average_ticket'] or Decimal('0')

    last_bill = bills.first()
    last_bill_date = last_bill.date if last_bill else None

    today = timezone.now().date()
    spend_last_30 = bills.filter(date__gte=today - timedelta(days=30)).aggregate(total=Sum('total_price'))['total'] or Decimal('0')
    spend_last_365 = bills.filter(date__gte=today - timedelta(days=365)).aggregate(total=Sum('total_price'))['total'] or Decimal('0')

    top_items = list(
        BillItem.objects.filter(bill__client=client)
        .values('description')
        .annotate(total_quantity=Sum('quantity'), total_amount=Sum('amount'))
        .order_by('-total_amount')[:5]
    )

    recent_bills = list(bills[:6])
    revenue_trend = list(
        bills.values('date').annotate(total=Sum('total_price')).order_by('date')
    )

    context = {
        'client': client,
        'bills': bills,
        'bill_count': bill_count,
        'total_revenue': total_revenue,
        'total_quantity': total_quantity,
        'avg_bill': avg_bill,
        'last_bill_date': last_bill_date,
        'spend_last_30': spend_last_30,
        'spend_last_365': spend_last_365,
        'top_items': top_items,
        'recent_bills': recent_bills,
        'revenue_trend': revenue_trend,
        'client_form': ClientForm(instance=client),
        'current_store': store,
        'stores': store_qs,
    }
    return render(request, 'core/clients/client-bills.html', context)

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
    
    # Check for special parameters
    show_geo = request.GET.get("show_geo") == "1"
    debug = request.GET.get("debug") == "1"
    
    store, store_qs = get_current_store(request)

    # Check cache first (but skip cache if special parameters are present)
    cache_key = f"dashboard_{user.id}_{store.id if store else 'all'}"
    if not show_geo and not debug:
        cached_data = cache.get(cache_key)
        if cached_data:
            return render(request, 'core/statistics/dashboard.html', cached_data)
    
    # Filter data for current user
    bills = Bill.objects.filter(store_name=user)
    products = Product.objects.filter(user=user)
    clients = Client.objects.filter(user=user)
    if store:
        bills = bills.filter(store=store)
        products = products.filter(store=store)
        clients = clients.filter(store=store)
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
        'quantity': [format_decimal_value(p['qty']) for p in top_products_data]
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
            'quantity': [format_decimal_value(item['quantity']) for item in today_data]
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
            'items': format_decimal_value(bill.quantity)
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
        'values': [format_decimal_value(item['qty']) for item in pie_data]
    })
    timings["pie_chart"] = round((time.perf_counter() - t_start) * 1000)

    line_chart = monthly_chart

    # Optional geocoding with caching (only when requested)
    geo_data = None
    map_chart = None
    if show_geo:
        geo_cache_key = f"geo_data_{user.id}"
        geo_data = cache.get(geo_cache_key)
        if not geo_data:
            geolocator = Nominatim(user_agent="store_performance_dashboard")
            locations = []
            client_list = Client.objects.filter(user=user)
            if store:
                client_list = client_list.filter(store=store)
            client_list = client_list.only(
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
                    except Exception as e:
                        logger.warning(f"Geocoding failed for {location_str}: {str(e)}")
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
        "debug": debug,
        "timings": timings,
        "current_store": store,
        "stores": store_qs,
    }
    
    # Cache for 3 minutes (but not when special parameters are present)
    if not show_geo and not debug:
        cache.set(cache_key, context, 180)
    # Use the statistics dashboard template under templates/core/statistics/
    return render(request, 'core/statistics/dashboard.html', context)

@login_required(login_url='/login/')
def products(request):
    """Handle product listing and creation with proper validation."""
    store, store_qs = get_current_store(request)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Check if a new category name is provided
                new_category_name = request.POST.get('new_category', '').strip()
                if new_category_name and len(new_category_name) > 100:
                    messages.error(request, 'Category name must be less than 100 characters.')
                    form = ProductForm()
                else:
                    product = form.save(commit=False)  # Save the form temporarily without committing to the database
                    product.user = request.user  # Assign the current user to the product's user field

                    if new_category_name:
                        # Create a new category or get the existing one with the provided name
                        category, created = Category.objects.get_or_create(title=new_category_name)
                        product.category = category  # Assign the new or existing category to the product

                    if store:
                        product.store = store
                    product.save()  # Now save the product to the database
                    messages.success(request, 'Product saved successfully.')
                    logger.info(f"Product created by user {request.user.id}: {product.title}")
                    return redirect("core:products")  # Redirect to a new URL
            except Exception as e:
                logger.error(f"Error saving product: {str(e)}")
                messages.error(request, 'An error occurred while saving the product.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()

    products_qs = Product.objects.filter(user=request.user)
    if store:
        products_qs = products_qs.filter(store=store)
    product_count = products_qs.count()
    products = products_qs.order_by('-date')[:500]  # Limit to 500 recent products

    categories_qs = Category.objects.filter(product__user=request.user)
    if store:
        categories_qs = categories_qs.filter(product__store=store)
    categories_qs = categories_qs.distinct().order_by('title')
    category_count = categories_qs.count()
    categories = categories_qs[:100]  # Limit categories to 100

    clients_qs = Client.objects.filter(user=request.user)
    if store:
        clients_qs = clients_qs.filter(store=store)
    client_count = clients_qs.count()
    clients = clients_qs.order_by('full_name')[:500]

    context = {
        'products': products,
        'categories': categories,
        'clients': clients,
        'form': form,
        'product_count': product_count,
        'client_count': client_count,
        'category_count': category_count,
        'current_store': store,
        'stores': store_qs,
    }

    return render(request, 'core/products/products.html', context)

@login_required(login_url='/login/')
@transaction.atomic
def create_bill(request):
    # For GET requests, render the multi-bill creation page
    store, store_qs = get_current_store(request)

    if request.method == 'GET':
        # Get all existing clients for the dropdown
        client_qs = Client.objects.filter(user=request.user)
        if store:
            client_qs = client_qs.filter(store=store)
        clients = list(client_qs.order_by('-id')[:50])
        client_total = client_qs.count()
        
        # Get last 10 created bills with related data
        bills_qs = Bill.objects.filter(store_name=request.user)
        if store:
            bills_qs = bills_qs.filter(store=store)
        recent_bills = bills_qs.select_related('client').prefetch_related('items').order_by('-date', '-id')[:10]

        products_qs_base = Product.objects.filter(user=request.user)
        if store:
            products_qs_base = products_qs_base.filter(store=store)
        products_qs = list(products_qs_base.select_related('category').order_by('title')[:300])
        product_total = products_qs_base.count()
        product_options = [
            {
                "id": product.id,
                "title": product.title,
                "price": format_decimal_value(product.price),
                "description": product.description or "",
                "category": product.category.title if product.category else "",
                "sku": product.sku,
            }
            for product in products_qs
        ]
        
        # Calculate statistics for dashboard
        bills_today_qs = Bill.objects.filter(
            store_name=request.user,
            date=timezone.now().date()
        )
        if store:
            bills_today_qs = bills_today_qs.filter(store=store)
        total_bills_today = bills_today_qs.count()
        
        total_revenue_today = bills_today_qs.aggregate(total=Sum('total_price'))['total'] or 0
        
        return render(request, 'core/clients/create-bill.html', {
            'user': request.user,
            'clients': clients,
            'recent_bills': recent_bills,
            'total_bills_today': total_bills_today,
            'total_revenue_today': total_revenue_today,
            'product_options': product_options,
            'product_count': product_total,
            'client_count': client_total,
            'current_store': store,
            'stores': store_qs,
        })

    # POST: Handle bill creation
    if request.method == 'POST':
        error_context = {'user': request.user, 'current_store': store, 'stores': store_qs}
        client_name = request.POST.get('clientName', '').strip()
        bill_date = request.POST.get('billDate')
        
        # Validate client name is not empty
        if not client_name or len(client_name) > 100:
            messages.error(request, 'Client name is required and must be less than 100 characters.')
            return render(request, 'core/clients/create-bill.html', error_context)

        # Parse bill items sent as JSON
        items_json = request.POST.get('items_json', '')
        try:
            items_data = json.loads(items_json) if items_json else []
        except json.JSONDecodeError:
            messages.error(request, 'Invalid items payload. Please try again.')
            logger.warning(f"JSONDecodeError in bill creation for user {request.user.id}")
            return render(request, 'core/clients/create-bill.html', error_context)

        if not items_data or len(items_data) == 0:
            messages.error(request, 'Please add at least one product to the bill.')
            return render(request, 'core/clients/create-bill.html', error_context)

        # Limit number of items to prevent abuse
        if len(items_data) > 1000:
            messages.error(request, 'Maximum 1000 items per bill.')
            return render(request, 'core/clients/create-bill.html', error_context)

        try:
            # Resolve or create client - now with more fields from multi-bill form
            client_select = request.POST.get('clientSelect', '').strip()
            if client_select:
                client_filters = {'lid': client_select, 'user': request.user}
                if store:
                    client_filters['store'] = store
                client = Client.objects.get(**client_filters)
                created = False
            else:
                # Check if client exists by name first
                existing_filters = {'full_name': client_name, 'user': request.user}
                if store:
                    existing_filters['store'] = store
                existing_client = Client.objects.filter(**existing_filters).first()
                
                if existing_client:
                    # Update existing client with new info if provided
                    client = existing_client
                    created = False
                    
                    # Safely update fields with validation
                    phone = request.POST.get('phone', '').strip()[:20]
                    email = request.POST.get('email', '').strip()[:100]
                    address = request.POST.get('address', '').strip()[:100]
                    city = request.POST.get('city', '').strip()[:100]
                    country = request.POST.get('country', '').strip()[:100]
                    postal_code = request.POST.get('postal_code', '').strip()[:10]
                    
                    if phone:
                        client.phone = phone
                    if email:
                        client.email = email
                    if address:
                        client.address = address
                    if city:
                        client.city = city
                    if country:
                        client.country = country
                    if postal_code:
                        client.postal_code = postal_code
                    
                    client.save()
                else:
                    # Create new client with validated data
                    client = Client.objects.create(
                        full_name=client_name[:100],
                        user=request.user,
                        store=store,
                        address=request.POST.get('address', '').strip()[:100],
                        phone=request.POST.get('phone', '').strip()[:20],
                        email=request.POST.get('email', '').strip()[:100],
                        city=request.POST.get('city', '').strip()[:100],
                        country=request.POST.get('country', '').strip()[:100],
                        postal_code=request.POST.get('postal_code', '').strip()[:10],
                    )
                    created = True

            parsed_items = []
            total_price = Decimal('0')
            total_qty = Decimal('0')

            for item in items_data:
                title = (item.get('title') or item.get('description') or '').strip()[:255]
                try:
                    price = Decimal(str(item.get('price', 0)))
                    qty = Decimal(str(item.get('quantity', 0)))
                except (InvalidOperation, ValueError):
                    messages.error(request, 'Invalid price or quantity format.')
                    return render(request, 'core/clients/create-bill.html', error_context)
                
                # Validate positive values
                if price < 0 or qty < 0:
                    messages.error(request, 'Price and quantity must be positive.')
                    return render(request, 'core/clients/create-bill.html', error_context)
                
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
            description_summary = ", ".join([p['description'] for p in parsed_items if p['description']])[:255]

            bill = Bill.objects.create(
                store_name=request.user,
                store=store,
                client=client,
                date=bill_date if bill_date else timezone.now().date(),
                quantity=total_qty,
                description=description_summary,
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
                messages.success(request, f'Bill saved successfully!')
            else:
                messages.success(request, f'Bill saved successfully!')

            logger.info(f"Bill created successfully for user {request.user.id} with {len(parsed_items)} items")

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
            logger.warning(f"Client not found for user {request.user.id}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Selected client not found.'}, status=400)
            messages.error(request, 'Selected client not found.')
            return render(request, 'core/clients/create-bill.html', error_context)
        except (ValueError, InvalidOperation) as ve:
            from django.http import JsonResponse
            logger.error(f"Invalid operation in bill creation: {str(ve)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Invalid data format.'}, status=400)
            messages.error(request, 'Invalid data format.')
            return render(request, 'core/clients/create-bill.html', error_context)
        except Exception as e:
            from django.http import JsonResponse
            logger.error(f"Error creating bill: {str(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'An error occurred.'}, status=500)
            messages.error(request, 'An error occurred while saving the bill.')
            return render(request, 'core/clients/create-bill.html', error_context)

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
    
    store, store_qs = get_current_store(request)

    # Check cache
    cache_key = f"reports_{user.id}_{store.id if store else 'all'}_{report_type}_{period}_{start_date.date()}_{end_date.date()}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'core/statistics/reports.html', cached_data)
    
    # Base queryset - filtered once, reused multiple times
    bills = Bill.objects.filter(store_name=user, date__gte=start_date, date__lte=end_date)
    if store:
        bills = bills.filter(store=store)
    
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
    ).only('title', 'price', 'stock', 'product_status', 'category_id')
    if store:
        product_performance = product_performance.filter(store=store)
    product_performance = product_performance.order_by('-price')[:10]
    
    # Client analysis - optimized with only()
    client_analysis = Client.objects.filter(user=user).annotate(
        total_spent=Sum('bill__total_price'),
        visit_count=Count('bill', distinct=True),
        avg_purchase=Avg('bill__total_price')
    ).only('full_name', 'email', 'phone')
    if store:
        client_analysis = client_analysis.filter(store=store)
    client_analysis = client_analysis.order_by('-total_spent')[:10]
    
    # Category breakdown - optimized
    category_breakdown = Category.objects.filter(product__user=user)
    if store:
        category_breakdown = category_breakdown.filter(product__store=store)
    category_breakdown = category_breakdown.annotate(
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
        'current_store': store,
        'stores': store_qs,
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, context, 300)
    return render(request, 'core/statistics/reports.html', context)
    
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
    return render(request, 'core/statistics/reports.html', context)

@login_required(login_url='/login/')
def settings(request):
    # Get user data and statistics
    user = request.user
    store, store_qs = get_current_store(request)
    product_qs = Product.objects.filter(user=user)
    client_qs = Client.objects.filter(user=user)
    bills_qs = Bill.objects.filter(store_name=user)
    if store:
        product_qs = product_qs.filter(store=store)
        client_qs = client_qs.filter(store=store)
        bills_qs = bills_qs.filter(store=store)
    user_products = product_qs.count()
    user_clients = client_qs.count()
    user_bills = bills_qs.count()
    total_revenue = bills_qs.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    context = {
        'user': user,
        'user_products': user_products,
        'user_clients': user_clients,
        'user_bills': user_bills,
        'total_revenue': total_revenue,
        'profile_image': user.image.url if user.image else None,
        'is_admin': user.is_staff or user.is_superuser,
        'current_store': store,
        'stores': store_qs,
    }
    return render(request, 'core/account/settings.html', context)

@login_required(login_url='/login/')
def profile(request):
    """View and edit user profile information"""
    user = request.user
    is_admin = user.is_staff or user.is_superuser
    store, store_qs = get_current_store(request)
    
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
        'current_store': store,
        'stores': store_qs,
    }
    return render(request, 'core/account/profile.html', context)


@login_required(login_url='/login/')
def stores_overview(request):
    """Summary dashboard. Staff see all stores; non-staff see only their store."""
    can_manage = request.user.is_staff or request.user.is_superuser

    base_qs = Store.objects.select_related('owner').annotate(
        total_revenue=Coalesce(
            Sum('bills__total_price', output_field=DecimalField()),
            Value(0, output_field=DecimalField())
        ),
        orders=Coalesce(
            Count('bills', distinct=True, output_field=IntegerField()),
            Value(0, output_field=IntegerField())
        ),
        last_activity=Max('bills__date'),
    )

    if can_manage:
        stores = base_qs.order_by('-total_revenue', 'name')
    else:
        stores = base_qs.filter(owner=request.user)

    store_cards = []
    for store in stores:
        orders = store.orders or 0
        revenue = store.total_revenue or Decimal('0')
        avg_order = revenue / orders if orders else Decimal('0')
        dashboard_url = f"{reverse('core:dashboard')}?store={store.slug}"
        card = {
            'id': store.id,
            'name': store.name,
            'status': store.status,
            'owner': store.owner,
            'slug': store.slug,
            'revenue': revenue,
            'orders': orders,
            'avg_order': avg_order,
            'last_activity': store.last_activity,
            'dashboard_url': dashboard_url,
        }
        if can_manage:
            card['admin_url'] = reverse('admin:core_store_change', args=[store.id])
        store_cards.append(card)

    total_revenue = sum(card['revenue'] for card in store_cards)
    total_orders = sum(card['orders'] for card in store_cards)
    avg_order_overall = (total_revenue / total_orders) if total_orders else Decimal('0')
    last_activity = max(
        (card['last_activity'] for card in store_cards if card['last_activity']),
        default=None
    )

    context = {
        'stores': store_cards,
        'create_store_url': reverse('admin:core_store_add') if can_manage else None,
        'can_manage': can_manage,
        'summary': {
            'count': len(store_cards),
            'revenue': total_revenue,
            'orders': total_orders,
            'avg_order': avg_order_overall,
            'last_activity': last_activity,
        },
    }
    # Use the newer template location under core/store/
    return render(request, 'core/store/stores_overview.html', context)


@login_required(login_url='/login/')
def store_create_redirect(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("You do not have permission to create stores.")
    return redirect('/admin/core/store/add/')


# Bill Actions
@login_required(login_url='/login/')
def edit_bill(request, bill_id):
    """Edit bill details"""
    try:
        store, _ = get_current_store(request)
        bill_filters = {'id': bill_id, 'store_name': request.user}
        if store:
            bill_filters['store'] = store
        bill = Bill.objects.get(**bill_filters)
        
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
        store, _ = get_current_store(request)
        bill_filters = {'id': bill_id, 'store_name': request.user}
        if store:
            bill_filters['store'] = store
        bill = Bill.objects.get(**bill_filters)
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
        store, _ = get_current_store(request)
        bill_filters = {'id': bill_id, 'store_name': request.user}
        if store:
            bill_filters['store'] = store
        bill = Bill.objects.get(**bill_filters)
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
        store, _ = get_current_store(request)
        bill_filters = {'id': bill_id, 'store_name': request.user}
        if store:
            bill_filters['store'] = store
        original_bill = Bill.objects.get(**bill_filters)
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

        store, _ = get_current_store(request)
        bill_filters = {'id': bill_id, 'store_name': request.user}
        if store:
            bill_filters['store'] = store
        bill = Bill.objects.get(**bill_filters)
        
        # Get bill items or create from legacy data
        items = []
        if bill.items.exists():
            items = [
                {
                    'id': item.id,
                    'description': item.description,
                    'quantity': format_decimal_value(item.quantity),
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
                'quantity': format_decimal_value(bill.quantity),
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
        
        store, _ = get_current_store(request)
        bill_filters = {'id': bill_id, 'store_name': request.user}
        if store:
            bill_filters['store'] = store
        bill = Bill.objects.get(**bill_filters)
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

        store, _ = get_current_store(request)
        products = Product.objects.filter(user=request.user)
        if store:
            products = products.filter(store=store)
        products = products.order_by('-date')[:100]
        
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
def create_client(request):
    """AJAX endpoint to add a new client to the portfolio."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    store, _ = get_current_store(request)
    form = ClientForm(request.POST)
    if form.is_valid():
        client = form.save(commit=False)
        client.user = request.user
        if store:
            client.store = store
        client.gpt5_enabled = parse_truthy(request.POST.get('gpt5_enabled'), default=True)
        client.save()

        response_data = {
            'lid': client.lid,
            'full_name': client.full_name,
            'email': client.email,
            'phone': client.phone,
            'city': client.city,
            'country': client.country,
            'gpt5_enabled': client.gpt5_enabled,
            'detail_url': reverse('core:client_detail', args=[client.lid]),
            'total_spend': format_decimal_value(0),
            'bill_count': 0,
        }
        return JsonResponse({'success': True, 'client': response_data})

    return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)


@login_required(login_url='/login/')
def update_client_info(request, lid):
    """Persist client profile updates via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    store, _ = get_current_store(request)
    client_filters = {'lid': lid, 'user': request.user}
    if store:
        client_filters['store'] = store
    client = get_object_or_404(Client, **client_filters)
    form = ClientForm(request.POST, instance=client)

    if form.is_valid():
        updated_client = form.save(commit=False)
        updated_client.gpt5_enabled = parse_truthy(request.POST.get('gpt5_enabled'), default=client.gpt5_enabled)
        updated_client.save()

        totals = Bill.objects.filter(client=updated_client).aggregate(
            total_spend=Sum('total_price'),
            bill_count=Count('id'),
            last_bill_date=Max('date')
        )

        response_data = {
            'lid': updated_client.lid,
            'full_name': updated_client.full_name,
            'email': updated_client.email,
            'phone': updated_client.phone,
            'address': updated_client.address,
            'city': updated_client.city,
            'country': updated_client.country,
            'postal_code': updated_client.postal_code,
            'gpt5_enabled': updated_client.gpt5_enabled,
            'total_spend': format_decimal_value(totals['total_spend'] or Decimal('0')),
            'bill_count': totals['bill_count'] or 0,
            'last_bill_date': totals['last_bill_date'],
        }

        return JsonResponse({'success': True, 'client': response_data})

    return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)


@login_required(login_url='/login/')
def update_client_picture(request):
    """Update client's profile picture"""
    if request.method == 'POST':
        client_lid = request.POST.get('client_lid')
        
        try:
            store, _ = get_current_store(request)
            client_filters = {'lid': client_lid, 'user': request.user}
            if store:
                client_filters['store'] = store
            client = Client.objects.get(**client_filters)
            
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
