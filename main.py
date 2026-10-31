from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.responses import FileResponse
import json
import sqlite3
app = FastAPI()

active_shuttles = {}
class ConnectionsManager:
    def __init__(self):
        #makes the list of all the active connections
        self.active_connections: List[WebSocket]=[]

    #to connect the new socket in the list
    async def connect(self,websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f" New Client connected. Total clients: {len(self.active_connections)}")

    #to remove the existing socket from the list    
    def disconnect(self,websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_json(self, data:dict):
        #send information to all the clients in the list
        for connection in self.active_connections:
            await connection.send_json(data)

# creating a cursor for shuttle.db
def get_db():
    conn = sqlite3.connect("shuttle.db")
    return conn

# to select the id,name,color from shuttle.db
def accessRoute():
    conn = get_db()
    lists= conn.execute("SELECT id,name,color FROM routes")
    routes = lists.fetchall()  
    list_routes=[]                
    for row in routes:
        id,name,color = row
        lists2 = conn.execute("SELECT route_id,name,latitude,longitude,stop_order " \
                    "FROM stops " \
                    "WHERE route_id = ? ORDER BY stop_order ASC",(id,)) 
        stops = lists2.fetchall()
        stops_list=[] ## first we are adding all the stop of route_1 or route_2 in stops and then we will add this stop dictionary into another dictionary for all the routes in dict_route
        for stop in stops:
            route_id, Name, latitude, longitude, stop_order = stop
            stops_list.append({"name":Name,"lat": latitude,"lng":longitude,"order":stop_order})

        list_routes.append({"id": id,"name":name, "color":color,"stops":stops_list})
    conn.close()
    return list_routes 

@app.get("/api/routes")
def get_routes():
    return accessRoute()

@app.get("/api/shuttles")
def get_shuttles():
    return active_shuttles

manager = ConnectionsManager()

@app.get("/health")
def health_check():
    return{
        "status":"online",
        "message": "Campus Shuttle Tracker "
    }


@app.get("/")
def serve_student_map():
    return FileResponse("index.html")

@app.get("/driver")
def serve_driver_console():
    return FileResponse("driver.html")

@app.websocket("/ws/shuttle")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
    
            shuttle_id = data.get("shuttle_id")
            active_shuttles[shuttle_id] = {
                "lat": data.get("lat"),
                "lng": data.get("lng"),
                "speed": data.get("speed"),
                "name": data.get("name"),
                "timestamp": data.get("timestamp"),
            }

            print(f" Received from client: {data}")

            # to send json instead of plain text
            await manager.broadcast_json(data)
    except WebSocketDisconnect :
        manager.disconnect(websocket)
        print("Client disconnected cleanly.")
