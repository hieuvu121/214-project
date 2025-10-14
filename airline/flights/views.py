from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic.list import ListView
from datetime import time

#demo data for searching flights
DEMO_FLIGHTS = [
    # airline, code, depart, arrive, origin, dest, duration_min, stops, price
    {"airline":"Virgin Australia","code":"VA882","depart":"19:00","arrive":"20:35","origin":"SYD","dest":"MEL","duration_min":95,"stops":0,"price":408},
    {"airline":"Qantas","code":"QF491","depart":"19:30","arrive":"21:05","origin":"SYD","dest":"MEL","duration_min":95,"stops":0,"price":385},
    {"airline":"Jetstar","code":"JQ533","depart":"19:45","arrive":"21:20","origin":"SYD","dest":"MEL","duration_min":95,"stops":0,"price":466},
    {"airline":"Qantas","code":"QF497","depart":"20:00","arrive":"21:35","origin":"SYD","dest":"MEL","duration_min":95,"stops":0,"price":372},
    {"airline":"Virgin Australia","code":"VA888","depart":"21:15","arrive":"22:50","origin":"SYD","dest":"MEL","duration_min":95,"stops":0,"price":359},
    {"airline":"Jetstar","code":"JQ539","depart":"21:30","arrive":"23:05","origin":"SYD","dest":"MEL","duration_min":95,"stops":0,"price":342},
    {"airline":"Qantas","code":"QF12","depart":"18:10","arrive":"21:10","origin":"SYD","dest":"MEL","duration_min":180,"stops":1,"price":315},
    {"airline":"Virgin Australia","code":"VA22","depart":"17:40","arrive":"20:00","origin":"SYD","dest":"MEL","duration_min":140,"stops":1,"price":298},
]

def _enrich_duration(flightList):
    for f in flightList:
        mins = f["duration_min"]
        f["dur_h"] = mins // 60
        f["dur_m"] = mins % 60
    return flightList

def flightList(request):
    trip=request.GET.get("trip",'oneway')
    origin=request.GET.get("origin",'SYD')
    dest=request.GET.get('dest','MEL')
    depart_date=request.GET.get('depart')
    return_date=request.GET.get('return')
    #for oneway flights will show flights that have
    outbound=[
        f for f in DEMO_FLIGHTS
        if f.get('origin')==origin and f.get("dest")==dest and (not depart_date or f.get('date')==depart_date)
    ]

    #flights showed for return selection
    inbound=[]
    if trip=='return' and return_date:
        inbound=[
            f for f in DEMO_FLIGHTS
            if f.get('origin')==origin and f.get("dest")==dest and (not depart_date or f.get('date')==depart_date)
        ]

    _enrich_duration(outbound)
    _enrich_duration(inbound)

    ctx = {
        "trip": trip,
        "origin": origin,
        "dest": dest,
        "depart_date": depart_date,
        "return_date": return_date,
        "outbound": outbound,
        "inbound": inbound,
        "airlines": sorted({f["airline"] for f in DEMO_FLIGHTS}),
    }

    return render(request,'flightList.html',ctx)

def search(request):
    q=request.GET.copy()

    required=['from','to','depart']
    if not all(q.get(k) for k in required):
        return redirect('home')
    
    base=reverse('flightList')
    return redirect(f'{base}?{q.urlencode()}')