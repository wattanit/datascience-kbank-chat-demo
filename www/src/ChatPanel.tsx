import { useEffect, useState, useRef } from "react";
import Grid from "@mui/joy/Grid";
import Sheet from "@mui/joy/Sheet";
import Button from "@mui/joy/Button";
import Switch from '@mui/joy/Switch';
import Typography from '@mui/joy/Typography';
import Markdown from 'react-markdown'
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
            <Markdown>
                {props.data.message}
            </Markdown>
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

function ChatPanel (props: StateProps & {
    chatId: number,
    setChatId: React.Dispatch<React.SetStateAction<number>>,
    showActivity: boolean, 
    setShowActivity: React.Dispatch<React.SetStateAction<boolean>>}) {
    let [messages, setMessages] = useState<ChatMessage[]>([]);
    let [chatTick, setChatTick] = useState<number>(0); // to force re-render
    let [chatStatus, setChatStatus] = useState<string>("init");

    let monitor = ()=>{
        if (chatStatus === "ask_context") {
            getContext();
        } else if (chatStatus === "ask_promotion") {
            getPromotion();
        } else if (chatStatus === "ask_response") {
            getResponse();
        }
    }

    let newChat = ()=>{
        let userName = props.state.currentUser?.name;
        let welcomeMessage = (userName)?{type: "system", message: "สวัสดีค่ะ คุณ"+userName+" มีอะไรให้ช่วยคะ"}:{type: "system", message: "สวัสดีค่ะ มีอะไรให้ช่วยคะ"};
        setMessages([welcomeMessage]);

        // create new thread
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({user_id: props.state.currentUser?.id})
        })
        .then(response => {return response.json()})
        .then(data => {
            props.setChatId(data.id);

            setChatStatus("done");
        })
    }

    let addMessage = (newMessage: string) => {
        let oldMessages = messages;
        let newMessages = [...oldMessages, {type: "user", message: newMessage}];
        setMessages(newMessages);

        // send message to server
        fetch('/api/chat/:id/message?id='+props.chatId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: props.state.currentUser?.id,
                message: newMessage
            })
        })
        .then(response => {return response.json()})
        .then(data => {
            setChatStatus("ask_context");
        })
    }

    let getContext = ()=>{
        if (chatStatus !== "ask_context") {
            return;
        }
        console.log("get context");

        fetch('/api/chat/:id/get_context?id='+props.chatId, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {return response.json()})
        .then(data => {
            console.log(data);
            if (data.action === "context_found") {
                setChatStatus("ask_promotion");
            }else if (data.action === "follow_up_question") {
                setChatStatus("done");
                let oldMessages = messages;
                let newMessages = [...oldMessages, {type: "bot", message: data.message}];
                setMessages(newMessages);
            }else if (data.action === "running") {
                // do nothing
            }else{
                setChatStatus("done");
                let oldMessages = messages;
                let newMessages = [...oldMessages, {type: "bot", message: "ขอโทษค่ะ ไม่เข้าใจคำถาม คุณสามารถลองถามใหม่อีกครั้งได้ค่ะ"}];
                setMessages(newMessages);
            }
        })
    }

    let getPromotion = ()=>{
        if (chatStatus !== "ask_promotion") {
            return;
        }
        setChatStatus("done");
        console.log("get promotion");

        fetch('/api/chat/:id/get_promotions?id='+props.chatId, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {return response.json()})
        .then(data => {
            console.log(data);
            if (data.action === "promotions found") {
                setChatStatus("ask_response");
            }else{
                setChatStatus("done");
                let oldMessages = messages;
                let newMessages = [...oldMessages, {type: "bot", message: "ขอโทษค่ะ ไม่พบโปรโมชั่นที่ตรงกับคำถาม คุณสามารถลองถามใหม่อีกครั้งได้ค่ะ"}];
                setMessages(newMessages);
            }
        })
    }

    let getResponse = ()=>{
        if (chatStatus !== "ask_response") {
            return;
        }
        console.log("get response");

        fetch('/api/chat/:id/get_response?id='+props.chatId, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {return response.json()})
        .then(data => {
            console.log(data);
            if (data.status === "done") {
                setChatStatus("done");

                // get last message with type "bot" and add new message
                let bot_messages = data.message.filter((message: ChatMessage)=>message.type === "bot");
                let latest_bot_message = bot_messages[bot_messages.length-1];
                console.log(latest_bot_message);

                let oldMessages = messages;
                let newMessages = [...oldMessages, {type: "bot", message: latest_bot_message.message}];
                setMessages(newMessages);

            }else if (data.status === "running") {
                // do nothing
            }else{
                setChatStatus("done");
                let oldMessages = messages;
                let newMessages = [...oldMessages, {type: "bot", message: "ขอโทษค่ะ ตอนนี้ระบบไม่สามารถให้ข้อมูลได้ คุณสามารถลองถามใหม่อีกครั้งได้ค่ะ"}];
                setMessages(newMessages);
            }
        })
    }

    useEffect(()=>{
        if (chatStatus === "init"){
            newChat();
        }
        
        monitor();
        setTimeout(()=>{
            if (chatTick < 1000000) {
                setChatTick(chatTick+1);
            }else{
                setChatTick(0);
            }
        }, 1500);

        return ()=>{
            // if (monitoringIntervalRef.current) {
            //     clearInterval(monitoringIntervalRef.current);
            // }
        }
    }, [chatTick]);
    
    return (
        <Grid xs={12} md={(props.showActivity)?8:12} sx={{
            paddingLeft: "1rem",
            paddingRight: "1rem",
        }}>
            <ChatPanelToolbar newChat={newChat} showActivity={props.showActivity} setShowActivity={props.setShowActivity} />
            <ChatWindow messages={messages}/>
            {(chatStatus !== "done")?<div>ระบบกำลังทำงานอยู่ กรุณารอสักครู่ ✨</div>:null}
            <ChatInputBar addMessage={addMessage}/>
        </Grid>
    )
}

export default ChatPanel;