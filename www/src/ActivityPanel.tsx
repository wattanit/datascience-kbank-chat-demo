import { useEffect, useState, useRef} from "react";
import Grid from "@mui/joy/Grid";
import { Sheet, Typography } from "@mui/joy";

function ActivityItem (props: {report: ActivityReport}) {
    let report_type = props.report.type;
    let report_message = props.report.message;

    if (report_type === "context_activity_found") {
        report_message = JSON.parse(report_message);
    }

    if (report_type === "promotions_found") {
        report_message = "Promotions found for the user";
    }


    return (
        <Sheet sx={{
            maxWidth: "90%",
            padding: "1rem",
            marginTop: "1rem",
            borderRadius: "0.5rem",
            border: "0.1rem solid rgba(1,200,50, 0.5)",
        }}>
            <b>{report_type}&nbsp;:&nbsp;</b>
            {report_message}
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
            maxHeight: "80vh",
            width: "100%",
        }}>
            {renderActivityItems}
        </Sheet>
    )
}

type ActivityReport = {
    type: string, // should be "system" or "AI"
    message: string,
}

function ActivityPanel (props : {chatId: number}) {
    let [activityReports, setActivityReports] = useState<ActivityReport[]>([]);

    let updateIntervalRef = useRef<NodeJS.Timeout|null>();

    let updateActivity = ()=>{
        // fetch activity reports from server
        fetch(`/api/chat/${props.chatId}/assistant`)
        .then(response => {return response.json()})
        .then(data => {
            setActivityReports(data);
        })
    }

    useEffect(()=>{
        if (updateIntervalRef.current) {
            clearInterval(updateIntervalRef.current);
        }

        if (props.chatId > 0) { 
            updateIntervalRef.current = setInterval(()=>{
                updateActivity();
            }, 1000);
        }

        return ()=>{
            if (updateIntervalRef.current) {
                clearInterval(updateIntervalRef.current);
            }
        }
    }, [props.chatId]);

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
            <ActivityWindow activityReports={activityReports}/>
        </Grid>
    )
}

export default ActivityPanel;