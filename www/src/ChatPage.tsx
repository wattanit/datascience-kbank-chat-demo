import { useState } from "react";
import Grid from "@mui/joy/Grid";
import ChatPanel from "./ChatPanel";
import ActivityPanel from "./ActivityPanel";
import { StateProps } from "./App";

function ChatPage (props: StateProps) {
    let [showActivity, setShowActivity] = useState(true);

    return (
        <Grid container spacing={1} sx={{
            flexGrow: 1,            
        }}>
            <ChatPanel {...props} showActivity={showActivity} setShowActivity={setShowActivity} />
            {(showActivity)?<ActivityPanel/>:null}
        </Grid>
    )
}

export default ChatPage;