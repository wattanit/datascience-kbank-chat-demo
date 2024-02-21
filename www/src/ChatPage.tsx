import Grid from "@mui/joy/Grid";
import ChatPanel from "./ChatPanel";
import ActivityPanel from "./ActivityPanel";


function ChatPage () {
    return (
        <Grid container spacing={1} sx={{
            flexGrow: 1,            
        }}>
            <ChatPanel/>
            <ActivityPanel/>
        </Grid>
    )
}

export default ChatPage;