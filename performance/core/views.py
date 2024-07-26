import pandas as pd
from core.models import *
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProductForm
from django.utils import timezone
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderInsufficientPrivileges

@login_required(login_url='/login/')
def analytics(request):
    return render(request, 'core/analytics.html')

@login_required(login_url='/login/')
def clients(request):
    clients = Client.objects.filter(user=request.user)

    context = {
        'clients': clients
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
    ######### Bar Chart #########
    today_bills = Bill.objects.filter(date=timezone.now().date())

    if today_bills.exists():
        product_descriptions = [bill.description for bill in today_bills]
        quantities_sold = [bill.quantity for bill in today_bills]
        fig = px.bar(x=product_descriptions, y=quantities_sold, title="Today's Sold Products")
        fig.update_layout(xaxis_title="Products", yaxis_title="Quantities")
        bar_chart = fig.to_html()
    else:
        bar_chart = None

    ######### Table Chart #########
    # Add table data
    if today_bills.exists():
        clients = [bill.client for bill in today_bills]
        products = [bill.description for bill in today_bills]
        quantities = [bill.quantity for bill in today_bills]
        total_price = [bill.total_price for bill in today_bills]
        table_data = [['Clients', 'Products', 'Quantity', 'Total Price']]
        for i in range(len(clients)):
            table_data.append([str(clients[i]), products[i], quantities[i], total_price[i]])

        # Initialize a figure with ff.create_table(table_data)
        fig = ff.create_table(table_data, height_constant=60)

        # Plot!
        table_chart = fig.to_html()
    else:
        table_chart = None

    ######### Pie Chart #########
    today_bills = Bill.objects.all()
    teams = [[str(bill.client), bill.description, bill.quantity] for bill in today_bills]

    df = pd.DataFrame({'Quantity': [quantity[2] for quantity in teams], 'Products': [product[1] for product in teams]})
    fig = px.pie(df, values='Quantity', names='Products', color='Products', title='Products Sold')

    pie_chart = fig.to_html()

    ######### Line Chart #########
    data = Bill.objects.filter(date__month=timezone.now().month)
    # Prepare data
    month = [d.date.strftime('%B') for d in data]
    products = [d.description for d in data]

    # Find the lowest and highest products
    lowest_product = min(products)
    highest_product = max(products)

    fig = go.Figure()

    # Create and style traces
    fig.add_trace(go.Scatter(x=month, y=products, name='Products Sold',
                            line=dict(color='firebrick', width=4, dash='dash')))
    fig.add_trace(go.Scatter(x=[month[products.index(lowest_product)]], y=[lowest_product], name='Lowest Product',
                            mode='markers', marker=dict(color='red', size=10)))
    fig.add_trace(go.Scatter(x=[month[products.index(highest_product)]], y=[highest_product], name='Highest Product',
                            mode='markers', marker=dict(color='green', size=10)))

    # Edit the layout
    fig.update_layout(title='High and Low Products Sold',
                    xaxis_title='Months',
                    yaxis_title='Products Sold')

    line_chart = fig.to_html()

    ######### Map Chart #########
    clients = Client.objects.all()
    teams = [[client.full_name, client.address] for client in clients]
    df = pd.DataFrame({'clients': [client[0] for client in teams], 'district': [address[1] for address in teams]})
    geojson = px.data.election_geojson()

    fig = px.choropleth_mapbox(df, geojson=geojson, color="clients",
                            locations="district", featureidkey="properties.district",
                            center={"lat": 33.518302, "lon": -7.595525},
                            mapbox_style="carto-positron", zoom=9)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    map_chart = fig.to_html()

    context = {
        'bar_chart': bar_chart,
        'table_chart': table_chart,
        'pie_chart': pie_chart,
        'line_chart': line_chart,
        'map_chart': map_chart,
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
def create_bill(request):
    if request.method == 'POST':
        client_name = request.POST.get('clientName')
        bill_date = request.POST.get('billDate')
        quantity = request.POST.get('quantity')
        description = request.POST.get('description')
        price = request.POST.get('price')
        amount = request.POST.get('amount')
        total_price = request.POST.get('totalPrice')
        
        # Check if client exists, otherwise create a new one
        client, created = Client.objects.get_or_create(name=client_name)
        
        # Save the bill
        bill = Bill(client=client, date=bill_date, quantity=quantity, description=description, price=price, amount=amount, total_price=total_price)
        bill.save()
        
        if created:
            return redirect('core:client_detail', lid=client.lid)
    else:
        return render(request, 'core/create-bill.html')

@login_required(login_url='/login/')
def reports(request):
    return render(request, 'core/reports.html')

@login_required(login_url='/login/')
def settings(request):
    return render(request, 'core/settings.html')
