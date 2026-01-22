"""
Analytics service layer: forecasting, segmentation, recommendations, anomaly detection.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, F, Value, DecimalField
from django.db.models.functions import Coalesce, TruncDate
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Centralized analytics business logic."""
    
    @staticmethod
    def get_kpis(store=None, start_date=None, end_date=None):
        """Compute KPIs for dashboard."""
        from core.models import Bill, Client, Product
        
        if not start_date:
            start_date = timezone.now().date() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()
        
        bills_qs = Bill.objects.filter(date__gte=start_date, date__lte=end_date)
        if store:
            bills_qs = bills_qs.filter(store=store)
        
        return {
            'total_revenue': float(bills_qs.aggregate(Sum('total_price'))['total_price__sum'] or 0),
            'total_quantity': bills_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0,
            'total_transactions': bills_qs.count(),
            'unique_customers': bills_qs.values('client').distinct().count(),
            'average_transaction_value': float(
                bills_qs.aggregate(
                    avg=Coalesce(
                        Sum('total_price') / Count('id'),
                        Value(0),
                        output_field=DecimalField()
                    )
                )['avg'] or 0
            ),
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
        }
    
    @staticmethod
    def get_trends(store=None, metric='revenue', days=90, granularity='day'):
        """Get metric trends over time."""
        from core.models import Bill, DailyMetric
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        bills_qs = Bill.objects.filter(date__gte=start_date, date__lte=end_date)
        if store:
            bills_qs = bills_qs.filter(store=store)
        
        data = bills_qs.extra(
            select={'date': f'DATE(date)'}
        ).values('date').annotate(
            revenue=Sum('total_price'),
            quantity=Sum('quantity'),
            count=Count('id')
        ).order_by('date')
        
        df = pd.DataFrame(list(data))
        if df.empty:
            return {'data': [], 'metric': metric, 'granularity': granularity}
        
        df['date'] = pd.to_datetime(df['date'])
        
        if granularity == 'week':
            df['period'] = df['date'].dt.to_period('W')
            df = df.groupby('period').agg({
                'revenue': 'sum',
                'quantity': 'sum',
                'count': 'sum'
            }).reset_index()
            df['period'] = df['period'].astype(str)
            df = df.rename(columns={'period': 'date'})
        elif granularity == 'month':
            df['period'] = df['date'].dt.to_period('M')
            df = df.groupby('period').agg({
                'revenue': 'sum',
                'quantity': 'sum',
                'count': 'sum'
            }).reset_index()
            df['period'] = df['period'].astype(str)
            df = df.rename(columns={'period': 'date'})
        
        key = 'revenue' if metric == 'revenue' else 'quantity' if metric == 'quantity' else 'count'
        
        return {
            'data': [
                {'date': row['date'], metric: float(row[key])}
                for _, row in df.iterrows()
            ],
            'metric': metric,
            'granularity': granularity,
        }
    
    @staticmethod
    def get_top_n(store=None, entity='clients', metric='revenue', limit=5):
        """Get top N clients/products by metric."""
        from core.models import Bill
        
        bills_qs = Bill.objects.filter(date__gte=timezone.now().date() - timedelta(days=90))
        if store:
            bills_qs = bills_qs.filter(store=store)
        
        if entity == 'clients':
            data = bills_qs.values('client__full_name').annotate(
                revenue=Sum('total_price'),
                quantity=Sum('quantity'),
                count=Count('id')
            ).order_by(f'-{metric}')[:limit]
            
            return [{
                'name': item['client__full_name'],
                metric: float(item[metric]),
                'transactions': item['count'],
            } for item in data]
        
        elif entity == 'products':
            data = bills_qs.values('description').annotate(
                revenue=Sum('total_price'),
                quantity=Sum('quantity'),
                count=Count('id')
            ).order_by(f'-{metric}')[:limit]
            
            return [{
                'name': item['description'],
                metric: float(item[metric]),
                'transactions': item['count'],
            } for item in data]
        
        return []
    
    @staticmethod
    def forecast_revenue(store=None, days=30):
        """Simple ARIMA forecast for revenue."""
        from core.models import Bill, Forecast
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=90)
        
        bills_qs = Bill.objects.filter(date__gte=start_date, date__lte=end_date)
        if store:
            bills_qs = bills_qs.filter(store=store)
        
        # Aggregate daily revenue
        daily_data = bills_qs.extra(
            select={'date': 'DATE(date)'}
        ).values('date').annotate(
            revenue=Sum('total_price')
        ).order_by('date')
        
        if len(daily_data) < 10:
            return {'error': 'Insufficient data for forecasting'}
        
        df = pd.DataFrame(list(daily_data))
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').asfreq('D', fill_value=0)
        
        try:
            model = ARIMA(df['revenue'], order=(1, 1, 1))
            model_fit = model.fit()
            forecast_result = model_fit.get_forecast(steps=days)
            forecast_df = forecast_result.conf_int()
            forecast_df['predicted'] = forecast_result.predicted_mean
            
            return {
                'forecasts': [
                    {
                        'date': idx.date().isoformat(),
                        'predicted': float(row['predicted']),
                        'lower': float(row[0]),
                        'upper': float(row[1]),
                    }
                    for idx, row in forecast_df.iterrows()
                ],
                'model': 'ARIMA(1,1,1)',
            }
        except Exception as e:
            logger.error(f"Forecast error: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def segment_customers(store=None):
        """RFM segmentation."""
        from core.models import Bill, Client
        
        end_date = timezone.now().date()
        
        bills_qs = Bill.objects.filter(date__lte=end_date)
        if store:
            bills_qs = bills_qs.filter(store=store)
        
        # RFM scores
        rfm_data = bills_qs.values('client__id', 'client__full_name').annotate(
            recency=Value(0),  # Placeholder
            frequency=Count('id'),
            monetary=Sum('total_price')
        )
        
        if not rfm_data:
            return {'segments': []}
        
        df = pd.DataFrame(list(rfm_data))
        if df.empty:
            return {'segments': []}
        
        # Normalize for clustering
        scaler = StandardScaler()
        features = scaler.fit_transform(df[['frequency', 'monetary']])
        
        # Simple k-means clustering
        if len(features) > 2:
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            df['segment'] = kmeans.fit_predict(features)
        else:
            df['segment'] = 0
        
        segment_names = {0: 'Standard', 1: 'Premium', 2: 'At-Risk'}
        
        return {
            'segments': [
                {
                    'cluster': int(row['segment']),
                    'name': segment_names.get(int(row['segment']), 'Other'),
                    'count': len(df[df['segment'] == row['segment']]),
                }
                for _, row in df.drop_duplicates('segment').iterrows()
            ],
            'customers': [
                {
                    'id': int(row['client__id']),
                    'name': row['client__full_name'],
                    'frequency': int(row['frequency']),
                    'monetary': float(row['monetary']),
                    'segment': segment_names.get(int(row['segment']), 'Other'),
                }
                for _, row in df.iterrows()
            ],
        }
    
    @staticmethod
    def detect_anomalies(store=None, metric='revenue'):
        """Detect anomalies using z-score."""
        from core.models import Bill, Anomaly
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=90)
        
        bills_qs = Bill.objects.filter(date__gte=start_date, date__lte=end_date)
        if store:
            bills_qs = bills_qs.filter(store=store)
        
        # Daily aggregation
        daily_data = bills_qs.extra(
            select={'date': 'DATE(date)'}
        ).values('date').annotate(
            revenue=Sum('total_price'),
            quantity=Sum('quantity')
        ).order_by('date')
        
        if not daily_data:
            return {'anomalies': []}
        
        df = pd.DataFrame(list(daily_data))
        col = 'revenue' if metric == 'revenue' else 'quantity'
        
        # Z-score calculation
        mean = df[col].mean()
        std = df[col].std()
        df['z_score'] = np.abs((df[col] - mean) / std)
        
        # Threshold: z-score > 2
        anomalies = df[df['z_score'] > 2]
        
        return {
            'anomalies': [
                {
                    'date': row['date'],
                    'value': float(row[col]),
                    'expected': float(mean),
                    'deviation': float((row[col] - mean) / mean * 100) if mean else 0,
                    'severity': 'high' if row['z_score'] > 3 else 'medium',
                }
                for _, row in anomalies.iterrows()
            ],
            'metric': metric,
        }
    
    @staticmethod
    def get_recommendations(client_id=None, product_id=None, limit=5):
        """Simple product recommendations: co-purchase + popularity."""
        from core.models import Bill, Product
        
        if product_id:
            # Products bought together with target product
            related_bills = Bill.objects.filter(
                description__isnull=False
            ).values('client').annotate(
                count=Count('id')
            ).filter(count__gt=1).values_list('client', flat=True)
            
            target_bills = Bill.objects.filter(
                product__pk=product_id
            ).values_list('client__id', flat=True)
            
            co_bills = Bill.objects.filter(
                client__id__in=target_bills
            ).filter(
                client__id__in=related_bills
            ).exclude(
                product__pk=product_id
            ).values('product__pk', 'product__title').annotate(
                count=Count('id'),
                avg_price=Sum('price') / Count('id')
            ).order_by('-count')[:limit]
            
            return [{
                'product_id': item['product__pk'],
                'name': item['product__title'],
                'frequency': item['count'],
                'avg_price': float(item['avg_price']),
            } for item in co_bills]
        
        # Popular products
        popular = Bill.objects.values('description').annotate(
            count=Count('id'),
            avg_price=Sum('price') / Count('id')
        ).order_by('-count')[:limit]
        
        return [{
            'name': item['description'],
            'frequency': item['count'],
            'avg_price': float(item['avg_price']),
        } for item in popular]
