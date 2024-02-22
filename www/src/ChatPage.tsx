import { useState } from "react";
import Grid from "@mui/joy/Grid";
import ChatPanel from "./ChatPanel";
import ActivityPanel from "./ActivityPanel";
import { StateProps } from "./App";

function ChatPage (props: StateProps) {
    let [showActivity, setShowActivity] = useState(true);
    let [chatId, setChatId] = useState<number>(0);

    return (
        <Grid container spacing={1} sx={{
            flexGrow: 1,            
        }}>
            <ChatPanel {...props} chatId={chatId} setChatId={setChatId} showActivity={showActivity} setShowActivity={setShowActivity} />
            {(showActivity)?<ActivityPanel chatId={chatId}/>:null}
        </Grid>
    )
}

export default ChatPage;