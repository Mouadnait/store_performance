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

@login_required(login_url='/login/')
def analytics(request):
    return render(request, 'core/analytics.html')

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
    bills = Bill.objects.filter(client=client)

    context = {
        'client': client,
        'bills': bills,
    }
    return render(request, 'core/client-bills.html', context)

@login_required(login_url='/login/')
def dashboard(request):
    # Filter data for current user
    bills = Bill.objects.filter(store_name=request.user).select_related('client')
    products = Product.objects.filter(user=request.user)
    clients = Client.objects.filter(user=request.user)
    
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
    
    kpis = {
        "total_revenue": total_revenue,
        "total_quantity": total_quantity,
        "total_clients": clients.count(),
        "total_products": products.count(),
        "today_revenue": today_revenue,
        "today_bills": today_bills_count,
        "month_revenue": month_revenue,
        "month_bills": month_bills_count,
        "avg_bill_value": (total_revenue / bills.count()) if bills.count() > 0 else 0,
    }

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
        ).to_html()

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
        ).to_html()

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
        ).to_html()

    # Today's bar chart (kept)
    bar_chart = None
    if today_bills.exists():
        product_descriptions = [bill.description for bill in today_bills]
        quantities_sold = [bill.quantity for bill in today_bills]
        fig = px.bar(x=product_descriptions, y=quantities_sold, title="Today's Sold Products")
        fig.update_layout(xaxis_title="Products", yaxis_title="Quantities")
        bar_chart = fig.to_html()

    # Table (recent bills)
    table_chart = None
    recent = bills.order_by("-date")[:10]
    if recent.exists():
        table_data = [["Client", "Product", "Qty", "Total Price", "Date"]]
        for b in recent:
            table_data.append([str(b.client), b.description, b.quantity, b.total_price, b.date])
        table_chart = ff.create_table(table_data, height_constant=40).to_html()

    # Pie: product share
    pie_chart = None
    pie_df = pd.DataFrame(list(bills.values("description").annotate(qty=Sum("quantity"))))
    if not pie_df.empty:
        pie_chart = px.pie(
            pie_df,
            values="qty",
            names="description",
            title="Product Share",
        ).to_html()

    # Line: monthly high/low simplified to trend already covered; keep original line as fallback
    line_chart = monthly_chart

    # Map (kept if data present)
    map_chart = None
    clients = Client.objects.all()
    if clients.exists():
        teams = [[c.full_name, c.address] for c in clients]
        df_map = pd.DataFrame({"clients": [c[0] for c in teams], "district": [a[1] for a in teams if a]})
        if not df_map.empty and not df_map["district"].isnull().all():
            geojson = px.data.election_geojson()
            fig = px.choropleth_mapbox(
                df_map,
                geojson=geojson,
                color="clients",
                locations="district",
                featureidkey="properties.district",
                center={"lat": 33.518302, "lon": -7.595525},
                mapbox_style="carto-positron",
                zoom=9,
            )
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            map_chart = fig.to_html()

    context = {
        "kpis": kpis,
        "bar_chart": bar_chart,
        "table_chart": table_chart,
        "pie_chart": pie_chart,
        "line_chart": line_chart,
        "map_chart": map_chart,
        "top_clients_chart": top_clients_chart,
        "top_products_chart": top_products_chart,
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

    products = Product.objects.filter(user=request.user, product_status="published", featured=True)
    # Fetch distinct categories
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
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
        
        # Get optional fields with defaults
        quantity = request.POST.get('quantity') or 0
        description = request.POST.get('description') or ''
        price = request.POST.get('price') or 0
        amount = request.POST.get('amount') or 0
        total_price = request.POST.get('totalPrice') or 0

        try:
            # Check if the client exists or create a new one
            client, created = Client.objects.get_or_create(
                full_name=client_name,
                user=request.user,
                defaults={
                    'address': request.POST.get('address', ''),
                    'phone': request.POST.get('phone', ''),
                    'email': request.POST.get('email', ''),
                }
            )

            # Create the bill and associate it with the client
            bill = Bill.objects.create(
                store_name=request.user,
                client=client,
                date=bill_date if bill_date else timezone.now().date(),
                quantity=int(quantity) if quantity else 0,
                description=description,
                price=float(price) if price else 0.0,
                amount=float(amount) if amount else 0.0,
                total_price=float(total_price) if total_price else 0.0
            )

            # Success message
            if created:
                messages.success(request, f'New client "{client_name}" created and bill saved successfully!')
            else:
                messages.success(request, f'Bill saved successfully for existing client "{client_name}"!')

            # Redirect to the clients page to see the client and their bills
            return redirect('core:clients')
            
        except ValueError as ve:
            messages.error(request, f'Invalid number format: {str(ve)}')
            return redirect(products_url)
        except Exception as e:
            messages.error(request, f'Error creating bill: {str(e)}')
            return redirect(products_url)

    # GET requests are redirected to the products page bill builder
    return redirect(products_url)

@login_required(login_url='/login/')
def reports(request):
    return render(request, 'core/reports.html')

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