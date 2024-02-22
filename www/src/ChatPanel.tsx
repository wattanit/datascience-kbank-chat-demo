import { useState } from "react";
import Grid from "@mui/joy/Grid";
import Sheet from "@mui/joy/Sheet";
import Button from "@mui/joy/Button";
import Switch from '@mui/joy/Switch';
import Typography from '@mui/joy/Typography';
import { StateProps } from "./App";

function ChatPanelToolbar(props: {newChat: ()=>void,showActivity: boolean, setShowActivity: React.Dispatch<React.SetStateAction<boolean>>}) {
    return (
        <Sheet sx={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "right",
            alignItems: "center",
        }}>
            <Typography component={"label"} sx={{marginRight: "1rem"}} endDecorator={
                <Switch color="neutral" variant="solid" checked={props.showActivity} onChange={(e)=>{props.setShowActivity(e.target.checked)}}/> 
            }>
                Show AI Activity ✨
            </Typography>
            <Button color="success" onClick={()=>{
                props.newChat();
            }}>เริ่มต้นคำถามใหม่</Button>
        </Sheet>
    )
}

function ChatInputBar (props: {addMessage: (newMessage: string)=>void}) {
    let [newMessage, setNewMessage] = useState("")

    return (
        <Sheet sx={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: "1rem",
        }}>
            <input type="text" style={{
                flexGrow: 1,
                padding: "0.5rem",
                border: "1px solid #ddd",
                borderRadius: "15px",
                fontSize: "16px",
                fontFamily: "Arial, sans-serif",
            }} value={newMessage} 
               onChange={(e)=>{setNewMessage(e.target.value)}}
               onKeyUp={(e)=>{
                // e.preventDefault();
                if (e.key === "Enter") {
                    props.addMessage(newMessage);
                    setNewMessage("");
                }
               }}
            />
            <Button color="success" onClick={()=>{
                props.addMessage(newMessage);
                setNewMessage("");
            }}>ส่งข้อความ</Button>
        </Sheet>
    )
}

function ChatBoxUser(props: {data: ChatMessage}) {
    return (
        <Sheet sx={{
            flexGrow: 0,
            marginTop: "1rem",
            border: "1px solid #ddd",
            borderRadius: '15px',
            padding: '10px',
            backgroundColor: '#E9F6FF',
            boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
            maxWidth: '70%',
            fontFamily: 'Arial, sans-serif',
            fontSize: '16px',
            lineHeight: '1.5',
            alignSelf: "flex-end",
        }}>
            {props.data.message}
        </Sheet>
    )
}

function ChatBoxSystem(props: {data: ChatMessage}) {
    return (
        <Sheet sx={{
            flexGrow: 0,
            marginTop: "1rem",
            border: "1px solid #ddd",
            borderRadius: '15px',
            padding: '10px',
            backgroundColor: '#CDFADB',
            boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
            maxWidth: '70%',
            fontFamily: 'Arial, sans-serif',
            fontSize: '16px',
            lineHeight: '1.5',
            alignSelf: "flex-start",
        }}>
            {props.data.message}
        </Sheet>
    )
}

type ChatMessage = {
    type: string,
    message: string,
}

function ChatWindow(props: {messages: ChatMessage[]}) {

    let renderMessages = props.messages.map((message, index)=>{
        if (message.type === "user") {
            return <ChatBoxUser key={index} data={message}/>
        } else if (message.type === "bot") {
            return <ChatBoxSystem key={index} data={message}/>
        } else {
            return <ChatBoxSystem key={index} data={message}/>
        }
    });

    return (
        <Sheet sx={{
            display: "flex",
            flexDirection: "column",
            overflowY: "auto",
            marginTop: "1rem",
            border: "1px solid #ddd",
            padding: '10px',
            backgroundColor: '#f9f9f9',
            height: "60vh",
        }}>
            {renderMessages}
        </Sheet>
    )
}

function ChatPanel (props: StateProps & {showActivity: boolean, setShowActivity: React.Dispatch<React.SetStateAction<boolean>>}) {
    let exampleMessages: ChatMessage[] = [
        {type: "user", message: "สวัสดีครับ"},
        {type: "system", message: "สวัสดีครับ มีอะไรให้ช่วยครับ"},
        {type: "user", message: "ฉันอยากทราบราคาสินค้า"},
        {type: "system", message: "ราคาสินค้าคือ 100 บาทครับ"},
        {type: "user", message: "ขอบคุณครับ"},
        {type: "system", message: "ยินดีครับ"},
    ]

    let [messages, setMessages] = useState(exampleMessages);

    let addMessage = (newMessage: string) => {
        let newMessages = [...messages, {type: "user", message: newMessage}];
        setMessages(newMessages);
    }

    let newChat = ()=>{
        let userName = props.state.currentUser?.name;
        let welcomeMessage = (userName)?{type: "system", message: "สวัสดีค่ะ คุณ"+userName+" มีอะไรให้ช่วยคะ"}:{type: "system", message: "สวัสดีค่ะ มีอะไรให้ช่วยคะ"};
        setMessages([welcomeMessage]);
    }
    
    return (
        <Grid xs={12} md={(props.showActivity)?8:12} sx={{
            paddingLeft: "1rem",
            paddingRight: "1rem",
        }}>
            <ChatPanelToolbar newChat={newChat} showActivity={props.showActivity} setShowActivity={props.setShowActivity} />
            <ChatWindow messages={messages}/>
            <ChatInputBar addMessage={addMessage}/>
        </Grid>
    )
}

export default ChatPanel;