import { useEffect, useState, useRef, JSXElementConstructor, ReactElement, ReactNode } from "react";
import Grid from "@mui/joy/Grid";
import Sheet from "@mui/joy/Sheet";
import Button from "@mui/joy/Button";
import Switch from '@mui/joy/Switch';
import Typography from '@mui/joy/Typography';
import CircularProgress from '@mui/joy/CircularProgress';
import { IoMdCheckmarkCircleOutline } from "react-icons/io";
import Markdown from 'react-markdown'
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { StateProps } from "./App";
import { JSX } from "react/jsx-runtime";

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
            <Button color="primary" onClick={()=>{
                props.newChat();
            }}>เริ่มต้นคำถามใหม่</Button>
        </Sheet>
    )
}

function ChatInputBar (props: {
    addMessage: (newMessage: string)=>void,
    chatStatus: string
}) {
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
               disabled={(props.chatStatus !== "ready")}
               onChange={(e)=>{setNewMessage(e.target.value)}}
               onKeyUp={(e)=>{
                // e.preventDefault();
                if (e.key === "Enter") {
                    props.addMessage(newMessage);
                    setNewMessage("");
                }
               }}
            />
            <Button color="primary" 
                disabled={(props.chatStatus !== "ready")}
                onClick={()=>{
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
            backgroundColor: '#FAF0D7',
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
            backgroundColor: '#CDF5FD',
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

function ChatBoxStatus(props: {chatAIStatus: ChatAIStatus}) {

    let analysis_status_indicator = (props.chatAIStatus.analysis)?<IoMdCheckmarkCircleOutline />:<CircularProgress color="primary" size="sm" />;
    let searching_status_indicator = (props.chatAIStatus.searching)?<IoMdCheckmarkCircleOutline />:<CircularProgress color="primary" size="sm" />;
    let promotion_found_indicator = (props.chatAIStatus.promotionFound)?<IoMdCheckmarkCircleOutline />:<CircularProgress color="primary" size="sm" />;

    let analysis_status = <>กำลังทำความเข้าใจคำถามของคุณ {analysis_status_indicator}</>;
    let searching_status = (props.chatAIStatus.analysis)?<>กำลังค้นหาโปรโมชั่น {searching_status_indicator}</> : null;
    let promotion_found_status = (props.chatAIStatus.searching)?<>กำลังคัดเลือกโปรโมชั่นที่เหมาะสม {promotion_found_indicator}</> : null;
    
    return (
        <Sheet sx={{
            flexGrow: 0,
            marginTop: "1rem",
            border: "1px solid #ddd",
            borderRadius: '15px',
            padding: '10px',
            backgroundColor: '#FDE2E4',
            boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
            maxWidth: '70%',
            fontFamily: 'Arial, sans-serif',
            fontSize: '16px',
            lineHeight: '1.5',
            alignSelf: "flex-start",
        }}>
            {analysis_status} 
            {(props.chatAIStatus.analysis)?<br/>:null}
            {searching_status}
            {(props.chatAIStatus.searching)?<br/>:null}
            {promotion_found_status}
        </Sheet>
    )
}

function ChatBoxInfo(props: {data: ChatMessage}) {
    return (
        <Sheet sx={{
            flexGrow: 0,
            marginTop: "1rem",
            border: "1px solid #ddd",
            borderRadius: '15px',
            padding: '10px',
            backgroundColor: '#dde0dd',
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

export type ChatMessage = {
    type: string,
    message: string,
    streaming: boolean,
}

type WebSocketMessage = {
    type: string,
    data: any,
}


function ChatWindow(props: {
    messages: ChatMessage[],
    chatAIStatus: ChatAIStatus
}) {

    let renderMessages: ReactElement<any, string | JSXElementConstructor<any>>[] | JSX.Element[] = [];
    props.messages.forEach((message, index)=>{
        if (message.type === "user") {
            renderMessages.push(<ChatBoxUser key={index} data={message}/>);
        }
        else if (message.type === "assistant") {
            renderMessages.push(<ChatBoxSystem key={index} data={message}/>);
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
            {(props.chatAIStatus.processing)?<ChatBoxStatus chatAIStatus={props.chatAIStatus}/>:null}
        </Sheet>
    )
}

type ChatAIStatus = {
    processing: boolean,
    analysis: boolean,
    searching: boolean,
    promotionFound: boolean,
}

export function ChatPanel (props: StateProps & {
    chatId: number,
    setChatId: React.Dispatch<React.SetStateAction<number>>,
    showActivity: boolean, 
    setShowActivity: React.Dispatch<React.SetStateAction<boolean>>,
    messages: ChatMessage[],
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>,
    socketUrl: string,
}) {
    let { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket<WebSocketMessage>(props.socketUrl, {
        onOpen: ()=> {console.log("ChatPanel: WebSocket connected")},
        onClose: ()=> {console.log("ChatPanel: WebSocket disconnected")},
        share: true,
    });

    let [chatAIStatus, setChatAIStatus] = useState<ChatAIStatus>({processing: false, analysis: false, searching: false, promotionFound: false}); // {analysis: false, searching: false

    // chatStatus controls the main event loop and should be one of the following:
    // init, running, ready
    let [chatStatus, setChatStatus] = useState<string>("init"); 
    
    // new chat event handler.
    let newChat = ()=>{
        let userName = props.state.currentUser?.name;
        let welcomeMessage = (userName)?{type: "assistant", message: "สวัสดีค่ะ คุณ"+userName+" สนใจหาโปรโมชั่นสำหรับโอกาสไหนคะ", streaming: false}:{type: "system", message: "สวัสดีค่ะ มีอะไรให้ช่วยคะ", streaming: false};
        props.setMessages([welcomeMessage]);

        // create new thread
        let request = {
            action: "create_new_chat",
            data: {
                user_id: props.state.currentUser?.id
            }
        }

        sendJsonMessage(request);
        setChatAIStatus({processing: false, analysis: false, searching: false, promotionFound: false});
    }

    // add message event handler. This function will add a new message to the chat thread and set chatStatus to "running"
    let addMessage = (newMessage: string) => {
        let oldMessages = props.messages;
        let newMessages = [...oldMessages, {type: "user", message: newMessage, streaming: false}];
        props.setMessages(newMessages);

        // send message to server
        let request = {
            action: "new_user_message",
            data: {
                chat_id: props.chatId,
                user_id: props.state.currentUser?.id,
                message: newMessage
            }
        }
        sendJsonMessage(request);
        setChatStatus("running");
        setChatAIStatus({...chatAIStatus, processing: true});
    }

    useEffect(()=>{
        console.log("chat status: "+chatStatus);
        if (chatStatus === "init"){
            if (readyState === ReadyState.OPEN) {
                newChat();
            }
        }

        if (lastJsonMessage !== null && readyState === ReadyState.OPEN){
            if (lastJsonMessage.type === "new_chat_info") {
                let chatId = lastJsonMessage.data.chat_id;
                props.setChatId(chatId);

                setChatStatus("ready");
            }     
            else if (lastJsonMessage.type === "chat") {
                let message_type = lastJsonMessage.data.message_type;
                let message = lastJsonMessage.data.message;

                if (message_type === "system"){
                    let oldMessages = props.messages;
                    let newMessages = [...oldMessages, {type: "system", message: message, streaming: false}];
                    props.setMessages(newMessages);
                    setChatStatus("running");
                    if (message === "AI ของเราเข้าใจคำถามของคุณแล้ว กรุณารอสักครู่"){
                        setChatAIStatus({...chatAIStatus, analysis: true});
                    }else if (message === "กำลังค้นหาโปรโมชั่นที่เหมาะสมสำหรับคุณ"){
                        setChatAIStatus({...chatAIStatus, searching: true});
                    }else{
                        setChatAIStatus({...chatAIStatus, promotionFound: true});
                    }
                }else if(message_type === "assistant"){
                    let oldMessages = props.messages;
                    let newMessages = [...oldMessages, {type: "assistant", message: message, streaming: false}];
                    props.setMessages(newMessages);
                    setChatStatus("ready");
                    setChatAIStatus({processing: false, analysis: false, searching: false, promotionFound: false});
                }
            }
            else if (lastJsonMessage.type === "chat_delta") {
                let message_type = lastJsonMessage.data.message_type;
                let message = lastJsonMessage.data.message;

                // keep only english and thai characters in the message
                message = message.replace(/[^a-zA-Z0-9ก-๙ ]/g, '');
                
                if (props.messages.length > 0 ){
                    let oldMessages = props.messages;

                    let last_message = oldMessages[oldMessages.length-1];
                    if (last_message.streaming){
                        if (lastJsonMessage.data.is_completed){
                            // streaming is completed, remove the last streamed message
                            let newMessages = [...oldMessages.slice(0, -1)];
                            props.setMessages(newMessages);
                        }else{
                            // streaming is not completed, append the message to the last streamed message
                            let newMessage = {type: message_type, message: last_message.message + message, streaming: true};
                            let newMessages = [...oldMessages.slice(0, -1), newMessage];
                            props.setMessages(newMessages);
                        }
                    }else{
                        // create a new streamed message
                        let newMessage = {type: message_type, message: message, streaming: true};
                        let newMessages = [...oldMessages, newMessage];
                        props.setMessages(newMessages);
                    }
                }
                setChatStatus("running");
            }
        }
    }, [readyState, lastJsonMessage]);
    
    return (
        <Grid xs={12} md={(props.showActivity)?8:12} sx={{
            paddingLeft: "1rem",
            paddingRight: "1rem",
        }}>
            <ChatPanelToolbar newChat={newChat} showActivity={props.showActivity} setShowActivity={props.setShowActivity} />
            <ChatWindow messages={props.messages} chatAIStatus={chatAIStatus}/>
            {(chatStatus !== "ready")?<div>ระบบกำลังทำงานอยู่ กรุณารอสักครู่ ✨</div>:null}
            <ChatInputBar addMessage={addMessage} chatStatus={chatStatus}/>
        </Grid>
    )
}

export default ChatPanel;