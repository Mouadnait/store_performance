/**
 * ============================================================
 * DASHBOARD - Charts and Map Initialization
 * ============================================================
 * 
 * Chart.js visualizations and Leaflet map with client locations
 */

// Display current date
document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});

// Chart.js default configuration
Chart.defaults.font.family = 'Inter, sans-serif';
Chart.defaults.color = '#6b7280';

// Top Clients Chart
if (typeof window.topClientsChart !== 'undefined') {
    (function() {
        const data = window.topClientsChart;
        const ctx = document.getElementById('topClientsChart');
        if (ctx && data.labels && data.revenue) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Revenue ($)',
                        data: data.revenue,
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return '$' + context.parsed.y.toFixed(2);
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(0);
                                }
                            }
                        }
                    }
                }
            });
        }
    })();
}

// Top Products Chart
if (typeof window.topProductsChart !== 'undefined') {
    (function() {
        const data = window.topProductsChart;
        const ctx = document.getElementById('topProductsChart');
        if (ctx && data.labels && data.quantity) {
            const quantityData = data.quantity.map(value => parseFloat(value));
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Quantity Sold',
                        data: quantityData,
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderColor: 'rgba(16, 185, 129, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        }
    })();
}

// Monthly Trend Chart
if (typeof window.lineChart !== 'undefined') {
    (function() {
        const data = window.lineChart;
        const ctx = document.getElementById('monthlyTrendChart');
        if (ctx && data.labels && data.revenue) {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Monthly Revenue ($)',
                        data: data.revenue,
                        borderColor: 'rgba(99, 102, 241, 1)',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return '$' + context.parsed.y.toFixed(2);
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(0);
                                }
                            }
                        }
                    }
                }
            });
        }
    })();
}

// Today's Sales Chart
if (typeof window.barChart !== 'undefined') {
    (function() {
        const data = window.barChart;
        const ctx = document.getElementById('todaySalesChart');
        if (ctx && data.labels && data.quantity) {
            const quantityData = data.quantity.map(value => parseFloat(value));
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Quantity',
                        data: quantityData,
                        backgroundColor: 'rgba(245, 158, 11, 0.8)',
                        borderColor: 'rgba(245, 158, 11, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        }
    })();
}

// Product Share Pie Chart
if (typeof window.pieChart !== 'undefined') {
    (function() {
        const data = window.pieChart;
        const ctx = document.getElementById('productShareChart');
        if (ctx && data.labels && data.values) {
            const valuesData = data.values.map(value => parseFloat(value));
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: valuesData,
                        backgroundColor: [
                            'rgba(99, 102, 241, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(239, 68, 68, 0.8)',
                            'rgba(139, 92, 246, 0.8)',
                            'rgba(236, 72, 153, 0.8)',
                            'rgba(14, 165, 233, 0.8)',
                            'rgba(34, 197, 94, 0.8)'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                boxWidth: 12,
                                padding: 10,
                                font: {
                                    size: 11
                                }
                            }
                        }
                    }
                }
            });
        }
    })();
}

// Recent Bills Table
if (typeof window.tableChart !== 'undefined') {
    (function() {
        const data = window.tableChart;
        const tbody = document.getElementById('recentBillsBody');
        if (tbody && data && data.length > 0) {
            data.forEach(function(bill) {
                const tr = document.createElement('tr');
                tr.innerHTML = 
                    '<td>' + bill.date + '</td>' +
                    '<td>' + bill.client + '</td>' +
                    '<td>$' + bill.total.toFixed(2) + '</td>' +
                    '<td>' + bill.items + '</td>';
                tbody.appendChild(tr);
            });
        }
    })();
}

// Initialize map with client locations
if (typeof window.geoData !== 'undefined' && typeof window.showGeo !== 'undefined' && window.showGeo) {
    (function() {
        const clientData = window.geoData;
        const mapElement = document.getElementById('client-map');
        
        if (mapElement && clientData && clientData.length > 0) {
            // Calculate center point from all clients
            let centerLat = 33.5731, centerLon = -7.5898; // Default Morocco
            if (clientData.length > 0) {
                const avgLat = clientData.reduce((sum, c) => sum + c.lat, 0) / clientData.length;
                const avgLon = clientData.reduce((sum, c) => sum + c.lon, 0) / clientData.length;
                centerLat = avgLat;
                centerLon = avgLon;
            }
            
            // Initialize Leaflet map centered on average client location
            const map = L.map('client-map').setView([centerLat, centerLon], 8);
            
            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);
            
            // Add markers for each client with actual geocoded coordinates
            const markers = [];
            const colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen'];
            
            clientData.forEach(function(client, index) {
                const markerColor = colors[index % colors.length];
                
                // Create custom colored marker
                const customIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-' + markerColor + '.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                
                // Use actual geocoded coordinates
                const marker = L.marker([client.lat, client.lon], {
                    icon: customIcon,
                    title: client.name
                }).bindPopup(
                    '<div style="text-align:center; min-width:200px;">' +
                    '<img src="' + client.profile_image + '" alt="' + client.name + '" style="width:80px; height:80px; border-radius:50%; border:3px solid #667eea; object-fit:cover; margin-bottom:8px;">' +
                    '<div style="font-weight:600; color:#1f2937; font-size:1em; margin-bottom:4px;">' + client.name + '</div>' +
                    '<div style="color:#6b7280; font-size:0.9em; margin-bottom:8px;">' + client.location + '</div>' +
                    (client.city ? '<div style="color:#9ca3af; font-size:0.85em;">🏙️ ' + client.city + '</div>' : '') +
                    (client.address ? '<div style="color:#9ca3af; font-size:0.85em;">📍 ' + client.address + '</div>' : '') +
                    (client.phone ? '<div style="color:#9ca3af; font-size:0.85em;">📞 ' + client.phone + '</div>' : '') +
                    '<div style="margin-top:10px;"><a href="/client/' + client.lid + '/" style="color:#667eea; text-decoration:none; font-weight:600; font-size:0.9em;">View & Update</a></div>' +
                    '</div>'
                ).addTo(map);
                
                markers.push(marker);
            });
            
            // Auto-fit map bounds to show all markers
            if (markers.length > 0) {
                const group = new L.featureGroup(markers);
                map.fitBounds(group.getBounds().pad(0.1));
            }
        }
    })();
}
