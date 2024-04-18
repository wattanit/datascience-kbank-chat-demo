import { useEffect, useState, useRef} from "react";
import Grid from "@mui/joy/Grid";
import { Sheet, Typography } from "@mui/joy";
import useWebSocket, { ReadyState } from 'react-use-websocket';

function ActivityItem (props: {report: ActivityReport}) {
    let report_header = props.report.header;
    let report_message = props.report.message;
    let response_time = props.report.response_time;

    if (report_header === "promotions_found") {
        report_message = "Promotions found for the user";
    }

    return (
        <Sheet sx={{
            maxWidth: "90%",
            padding: "1rem",
            marginTop: "1rem",
            borderRadius: "0.5rem",
            border: "0.1rem solid #78C1F3",
        }}>
            <b>{report_header}&nbsp;:&nbsp;</b>
            {report_message}
            <br />
            <Typography sx={{fontSize: "0.8em", fontStyle: "italic"}}>
                elasped time: {response_time}
            </Typography>
        </Sheet> 
    )
}

function ActivityWindow(props: {activityReports: ActivityReport[]}) {

    let renderActivityItems = props.activityReports.map((report, index)=>{
        return <ActivityItem key={index} report={report}/>
    });

    return (
        <Sheet sx={{
            flexGrow: 1,
            display: "flex",
            flexDirection: "column",
            padding: "1rem",
            textAlign: "right",
            alignContent: "right",
            justifyContent: "flex-start",
            overflowY: "auto",
            alignItems: "flex-end",
            maxHeight: "70vh",
            width: "100%",
        }}>
            {renderActivityItems}
        </Sheet>
    )
}

export type ActivityReport = {
    type: string, // should be "system" or "AI"
    header: string,
    message: string,
    response_time: number
}

type WebSocketMessage = {
    type: string,
    data: any,
}

export function ActivityPanel (props : {
    chatId: number,
    activityReports: ActivityReport[],
    setActivityReports: React.Dispatch<React.SetStateAction<ActivityReport[]>>,
    socketUrl: string,
}) {
    let { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket<WebSocketMessage>(props.socketUrl, {
        onOpen: ()=> {console.log("ActivityPanel: WebSocket connected")},
        onClose: ()=> {console.log("ActivityPanel: WebSocket disconnected")},
        share: true,
    });

    useEffect(()=>{
        if (lastJsonMessage !== null && readyState === ReadyState.OPEN){
            let message = lastJsonMessage;
            if (message.type === "activity") {
                let newReport: ActivityReport = {
                    type: "AI",
                    header: message.data.message_header,
                    message: message.data.message_body,
                    response_time: message.data.elasped_time,
                }
                props.setActivityReports([...props.activityReports, newReport]);
            }
        }
    }, [readyState, lastJsonMessage]);

    return (
        <Grid xs={12} md={4} sx={{            
            paddingLeft: "1rem",
            paddingRight: "1rem",
            borderLeft: "1px solid #01A950",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
        }}>
            <Typography level="h2" fontSize="xl" sx={{ mb: 0.5 }}>
                AI Activity Report
            </Typography>
            <ActivityWindow activityReports={props.activityReports}/>
        </Grid>
    )
}

export default ActivityPanel;