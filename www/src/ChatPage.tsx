import { useEffect, useState } from "react";
import Grid from "@mui/joy/Grid";
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { ChatPanel, ChatMessage } from "./ChatPanel";
import { ActivityPanel, ActivityReport } from "./ActivityPanel";
import { StateProps } from "./App";

function ChatPage (props: StateProps) {
    let [showActivity, setShowActivity] = useState(true);
    let [chatId, setChatId] = useState<number>(0);
    let [messages, setMessages] = useState<ChatMessage[]>([]);
    let [activityReports, setActivityReports] = useState<ActivityReport[]>([]);
    let [socketUrl, _] = useState<string>("ws://localhost:8000/api/chat-socket");
    let { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl, {
        onOpen: ()=> {console.log("WebSocket connected")},
        onClose: ()=> {console.log("WebSocket disconnected")},
        share: true,
    });

    return (
        <Grid container spacing={1} sx={{
            flexGrow: 1,            
        }}>
            <ChatPanel {...props} 
                chatId={chatId} 
                setChatId={setChatId} 
                showActivity={showActivity} 
                setShowActivity={setShowActivity} 
                messages={messages}
                setMessages={setMessages}
                socketUrl={socketUrl}
                />
            {(showActivity)?<ActivityPanel 
                chatId={chatId}
                activityReports={activityReports}
                setActivityReports={setActivityReports}
                socketUrl={socketUrl}
                />:null}
        </Grid>
    )
}

export default ChatPage;