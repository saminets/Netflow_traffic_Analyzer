import os,sys
import threading
import traceback
import asyncio,json
from fastapi.responses import HTMLResponse,PlainTextResponse

from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException,Depends
from api.routes.nta_collector.utils.snmp_collectors import SnmpCollector
from api.routes.nta_collector.utils.socket_manager import ConnectionManager
import pandas as pd
from datetime import datetime, timedelta


# from app.core.config import *
router = APIRouter(
    prefix="/nta_snmp_collector",
    tags=["nta_snmp_collector"],
)






manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    # Optionally process incoming data from clients if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)



@router.post('/ws/get_test')
async def test_get_nta_device_stats(
    message: str,
    ws_manager: ConnectionManager = Depends(lambda: manager)
):
    await ws_manager.send_message(message)
    return {"status": "Notification sent"}


interface_dataframe = pd.DataFrame()




@router.post('/ws/get_nta_device_stats')
async def test_get_nta_device_stats(
    ip_address: str = Query(..., description="IP address of the device"),
    device_type: str = Query(None, description="Name of the device"),
    community: str = Query("active", description="Device status (e.g., active, inactive)"),
    port: int = Query(..., ge=1, le=65535, description="Port number (1-65535)"),
    snmp_version: str = Query("active", description="Device status (e.g., active, inactive)"),
    collector_data: str = Query("interface", description="Device status (e.g., all, interface)"),
    ws_manager: ConnectionManager = Depends(lambda: manager)
):
    try:
        while True:
            # nta_device_stats = SnmpCollector()

            # # Retrieve SNMP data
            # nta_device_stats_data = nta_device_stats.getSnmpData(
            #     community=community,
            #     port=port,
            #     snmp_version=snmp_version,
            #     device_type=device_type,
            #     ip_address=ip_address,
            #     collector_data=collector_data, 
            # )

            await ws_manager.send_message(str({"message":"test"}))

            # Return success response
            # return {"status": "Notification sent", "data": nta_device_stats_data}
    except Exception as e:
        # Log the error and send an error response
        traceback.print_exc()
        await ws_manager.send_message(f"Error: {str(e)}")
        return {"status": "Error occurred", "details": str(e)}


def convert_datetimes(obj):
    if isinstance(obj, dict):  # Check if the object is a dictionary
        # Recursively process each key-value pair
        return {k: convert_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):  # If it's a list, apply conversion to each item
        return [convert_datetimes(item) for item in obj]
    elif isinstance(obj, datetime):  # If it's a datetime object, convert to string
        return obj.isoformat()
    else:
        return obj  # Return the object as-is if it's not a datetime

import time
@router.websocket("/ws/get_nta_device_interface_stats")
async def websocket_get_nta_device_stats(
    websocket: WebSocket
):
    await websocket.accept()  # Accept WebSocket connection

    try:
        global interface_dataframe
        params = await websocket.receive_text()  
        params = eval(params)  


        ip_address = params.get("ip_address")
        device_type = params.get("device_type")
        community = params.get("community", "active")
        port = params.get("port")
        snmp_version = params.get("snmp_version", "v1/v2")
        collector_data = params.get("collector_data", "interface")

        valid_snmp_versions = ["v1/v2", "v3"]
        valid_collector_Data = ['All','interface']
        if snmp_version not in valid_snmp_versions:
            error_message = f"Invalid SNMP version: {snmp_version}. Allowed values are {valid_snmp_versions}."
            await websocket.send_text(error_message)
            return  
        if collector_data not in valid_collector_Data:
            error_message = f"Invalid collector version: {collector_data}. Allowed values are {valid_collector_Data}."
            await websocket.send_text(error_message)
            return  

        while True:
            nta_device_stats = SnmpCollector()

            nta_device_stats_data = nta_device_stats.getSnmpData(
                community=community,
                port=port,
                snmp_version=snmp_version,
                device_type=device_type,
                ip_address=ip_address,
                collector_data=collector_data,
            )

            stats = nta_device_stats_data.get('interfaces', {})
            print("stats are:::::::::::::::::@@",stats)
            devices_data = nta_device_stats_data.get('device', {})
            timestamp = stats.pop("datetime")  

            flattened_data = [
                {
                    "interface_id": key,
                    "name": value["name"],
                    "status": value["status"],
                    "description": value["description"],
                    "download": value["download"],
                    "upload": value["upload"],
                    "datetime": pd.to_datetime(timestamp).isoformat(),  
                    "ip_address": ip_address,
                    "device_type": device_type
                }
                for key, value in stats.items() if key.isdigit()
            ]

            new_data_df = pd.DataFrame(flattened_data)
            

            interface_dataframe = pd.concat([interface_dataframe, new_data_df], ignore_index=True)

            # Calculate 1-minute averages
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            interface_dataframe["datetime"] = pd.to_datetime(interface_dataframe["datetime"], errors='coerce')
            filtered_df = interface_dataframe[interface_dataframe["datetime"] >= one_minute_ago]

            avg_df = (
                filtered_df.groupby("interface_id")
                .agg(
                    avg_upload=("upload", "mean"),
                    avg_download=("download", "mean"),
                    name=("name", "first"),
                    description=("description", "first"),
                    last_updated=("datetime", lambda x: max(pd.to_datetime(x)).isoformat()), 
                )
                .reset_index()
            )
            avg_data_json = avg_df.to_dict(orient="records")

            # Include device data if not empty
            if devices_data:
                avg_data_json.append({"device_data": devices_data})

            for record in avg_data_json:
                print("recordisss:", record)
    
                # Check if 'last_updated' exists and convert it to string
                if "last_updated" in record:
                    record["last_updated"] = str(record["last_updated"])
                    print("rrecord into str")
            print("avg data json",avg_data_json)

            avg_data_json = convert_datetimes(avg_data_json)
            await websocket.send_text(json.dumps(avg_data_json))

            # await asyncio.sleep(15)

    except WebSocketDisconnect:
        print("WebSocket disconnected", file=sys.stderr)
    except Exception as e:
        traceback.print_exc()
        await websocket.send_text(f"Error: {str(e)}")