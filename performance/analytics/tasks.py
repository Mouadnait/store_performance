"""
Celery tasks for analytics: forecasting, anomaly detection, segmentation, metrics aggregation.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .services import AnalyticsService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def compute_daily_forecasts(self):
    """Compute daily sales forecasts for all stores."""
    try:
        from core.models import Store, Forecast
        
        stores = Store.objects.filter(is_active=True)
        for store in stores:
            try:
                forecast_data = AnalyticsService.forecast_revenue(store=store, days=30)
                
                if 'error' not in forecast_data:
                    for item in forecast_data.get('forecasts', []):
                        Forecast.objects.update_or_create(
                            store=store,
                            metric='revenue',
                            forecast_date=item['date'],
                            defaults={
                                'predicted_value': item['predicted'],
                                'confidence_lower': item['lower'],
                                'confidence_upper': item['upper'],
                            }
                        )
                
                logger.info(f"Forecast computed for store {store.name}")
            except Exception as e:
                logger.error(f"Forecast error for store {store.name}: {e}")
        
        return {'status': 'success', 'stores_processed': stores.count()}
    
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def detect_daily_anomalies(self):
    """Detect anomalies in daily metrics."""
    try:
        from core.models import Store, Anomaly
        
        stores = Store.objects.filter(is_active=True)
        anomalies_found = 0
        
        for store in stores:
            try:
                anomaly_data = AnalyticsService.detect_anomalies(store=store, metric='revenue')
                
                for anomaly_item in anomaly_data.get('anomalies', []):
                    obj, created = Anomaly.objects.get_or_create(
                        store=store,
                        metric='revenue',
                        anomaly_date=anomaly_item['date'],
                        defaults={
                            'actual_value': anomaly_item['value'],
                            'expected_value': anomaly_item['expected'],
                            'deviation_percent': anomaly_item['deviation'],
                            'severity': anomaly_item['severity'],
                            'description': f"Revenue anomaly detected: {anomaly_item['deviation']:.1f}% deviation",
                        }
                    )
                    
                    if created:
                        anomalies_found += 1
                        logger.info(f"Anomaly created for {store.name}: {anomaly_item}")
                
                logger.info(f"Anomaly detection complete for {store.name}: {anomalies_found} new anomalies")
            
            except Exception as e:
                logger.error(f"Anomaly detection error for {store.name}: {e}")
        
        return {'status': 'success', 'anomalies_found': anomalies_found}
    
    except Exception as exc:
        logger.error(f"Anomaly detection task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def segment_customers(self):
    """Customer segmentation via RFM."""
    try:
        from core.models import Store
        
        stores = Store.objects.filter(is_active=True)
        
        for store in stores:
            try:
                segmentation = AnalyticsService.segment_customers(store=store)
                
                # TODO: Store segmentation results in Redis cache or new model
                logger.info(f"Customer segmentation complete for {store.name}: {len(segmentation['segments'])} segments")
            
            except Exception as e:
                logger.error(f"Segmentation error for {store.name}: {e}")
        
        return {'status': 'success', 'stores_processed': stores.count()}
    
    except Exception as exc:
        logger.error(f"Segmentation task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True)
def compute_daily_metrics(self):
    """Aggregate and cache daily metrics."""
    try:
        from core.models import Store, Bill, DailyMetric
        from django.db.models import Sum, Count
        
        today = timezone.now().date()
        stores = Store.objects.filter(is_active=True)
        
        for store in stores:
            bills = Bill.objects.filter(store=store, date=today)
            
            if bills.exists():
                metrics = {
                    'total_revenue': bills.aggregate(Sum('total_price'))['total_price__sum'] or 0,
                    'total_quantity': bills.aggregate(Sum('quantity'))['quantity__sum'] or 0,
                    'total_transactions': bills.count(),
                    'unique_customers': bills.values('client').distinct().count(),
                }
                
                if metrics['total_transactions'] > 0:
                    metrics['average_transaction_value'] = metrics['total_revenue'] / metrics['total_transactions']
                
                DailyMetric.objects.update_or_create(
                    store=store,
                    metric_date=today,
                    defaults=metrics
                )
        
        logger.info(f"Daily metrics computed for {stores.count()} stores")
        return {'status': 'success', 'date': today.isoformat()}
    
    except Exception as exc:
        logger.error(f"Daily metrics task failed: {exc}")
        return {'status': 'error', 'error': str(exc)}


@shared_task
def warm_cache():
    """Warm up Redis cache with frequently-accessed data."""
    try:
        from django.core.cache import cache
        from core.models import Store
        
        stores = Store.objects.filter(is_active=True)
        
        for store in stores:
            kpis = AnalyticsService.get_kpis(store=store)
            cache.set(f'kpis:{store.id}', kpis, timeout=3600)  # 1 hour
            
            trends = AnalyticsService.get_trends(store=store, metric='revenue', days=90)
            cache.set(f'trends:revenue:{store.id}', trends, timeout=3600)
        
        logger.info(f"Cache warmed for {stores.count()} stores")
        return {'status': 'success', 'stores': stores.count()}
    
    except Exception as exc:
        logger.error(f"Cache warming failed: {exc}")
        return {'status': 'error', 'error': str(exc)}
