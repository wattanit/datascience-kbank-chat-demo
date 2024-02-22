import { useState} from "react";
import Grid from "@mui/joy/Grid";
import { Sheet, Typography } from "@mui/joy";

function ActivityItem (props: {report: ActivityReport}) {
    return (
        <Sheet sx={{
            maxWidth: "90%",
            padding: "1rem",
            marginTop: "1rem",
            borderRadius: "0.5rem",
            border: "0.1rem solid rgba(1,200,50, 0.5)",
        }}>
            <b>{props.report.type}&nbsp;:&nbsp;</b>
            {props.report.message}
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

function ActivityPanel () {
    let exampleActivityReports: ActivityReport[] = [
        {
            type: "system",
            message: "User logged in"
        },
        {
            type: "AI",
            message: "AI started"
        },
    ]

    let [activityReports, setActivityReports] = useState<ActivityReport[]>(exampleActivityReports)

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