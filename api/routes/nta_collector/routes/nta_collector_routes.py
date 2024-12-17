import os,sys
import threading
import traceback

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

import time
@router.post('/ws/get_nta_device_interface_stats')
async def test_get_nta_device_stats(
    ip_address: str = Query(..., description="IP address of the device"),
    device_type: str = Query(None, description="Name of the device"),
    community: str = Query("active", description="Device status (e.g., active, inactive)"),
    port: int = Query(..., ge=1, le=65535, description="Port number (1-65535)"),
    snmp_version: str = Query("active", description="Device status (e.g., active, inactive)"),
    collector_data: str = Query("interface", description="Device status (e.g., all, interface)"),
    ws_manager: ConnectionManager = Depends(lambda: manager)
):
    global interface_dataframe  # Access the global DataFrame
    try:
        while True:
            nta_device_stats = SnmpCollector()

            # Retrieve SNMP data
            nta_device_stats_data = nta_device_stats.getSnmpData(
                community=community,
                port=port,
                snmp_version=snmp_version,
                device_type=device_type,
                ip_address=ip_address,
                collector_data=collector_data, 
            )

            # Extract the data into a DataFrame-friendly format
            stats = nta_device_stats_data[0]  # Assuming data is in the first element of the list
            timestamp = stats.pop("datetime")  # Remove and store the timestamp

            print("len of interface data frame is:",len(interface_dataframe),file=sys.stderr)
            flattened_data = [
                {
                    "interface_id": key,
                    "name": value["name"],
                    "status": value["status"],
                    "description": value["description"],
                    "download": value["download"],
                    "upload": value["upload"],
                    "datetime": pd.to_datetime(timestamp),  # Ensure timestamp is in datetime format
                    "ip_address": ip_address,  # Add context information
                    "device_type": device_type
                }
                for key, value in stats.items() if key.isdigit()
            ]

            # Convert to DataFrame and append to the global DataFrame
            new_data_df = pd.DataFrame(flattened_data)
            interface_dataframe = pd.concat([interface_dataframe, new_data_df], ignore_index=True)

            # Calculate 1-minute averages for upload and download
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            filtered_df = interface_dataframe[interface_dataframe["datetime"] >= one_minute_ago]

            avg_df = (
                filtered_df.groupby("interface_id")
                .agg(
                    avg_upload=("upload", "mean"),
                    avg_download=("download", "mean"),
                    name=("name", "first"),
                    description=("description", "first"),
                    last_updated=("datetime", "max"),
                )
                .reset_index()
            )

        # Send the average data to WebSocket clients
            value = "test"
            await ws_manager.send_message(avg_df.to_json(orient="records"))#avg_df.to_json(orient="records")
            time.sleep(15)
        # Return success response
        # return {
        #     "status": "Notification sent",
        #     "data": flattened_data,
        #     "averages": avg_df.to_dict(orient="records"),
        # }
    except Exception as e:
        # Log the error and send an error response
        traceback.print_exc()
        await ws_manager.send_message(f"Error: {str(e)}")
        return {"status": "Error occurred", "details": str(e)}