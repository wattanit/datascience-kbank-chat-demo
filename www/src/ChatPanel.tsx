import Grid from "@mui/joy/Grid";
import Sheet from "@mui/joy/Sheet";
import Button from "@mui/joy/Button";
import Switch from '@mui/joy/Switch';
import Typography from '@mui/joy/Typography';

function ChatPanelToolbar() {
    return (
        <Sheet sx={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "right",
            alignItems: "center",
        }}>
            <Typography component={"label"} sx={{marginRight: "1rem"}} endDecorator={
                <Switch color="neutral" variant="solid" checked={true}/> 
            }>
                Show AI Activity ✨
            </Typography>
            <Button color="success">เริ่มต้นคำถามใหม่</Button>
        </Sheet>
    )
}

function ChatInputBar () {
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
            }}/>
            <Button color="success">ส่งข้อความ</Button>
        </Sheet>
    )
}

function ChatBoxUser() {
    return (
        <Sheet sx={{
            flexGrow: 1,
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
            User
        </Sheet>
    )
}

function ChatBoxSystem() {
    return (
        <Sheet sx={{
            flexGrow: 1,
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
            System
        </Sheet>
    )
}

function ChatWindow() {
    return (
        <Sheet sx={{
            display: "flex",
            flexDirection: "column",
            overflowY: "auto",
            marginTop: "1rem",
            border: "1px solid #ddd",
            padding: '10px',
            backgroundColor: '#f9f9f9',
            maxHeight: "60vh",
        }}>
            <ChatBoxUser/>
            <ChatBoxSystem/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxUser/>
            <ChatBoxSystem/>
        </Sheet>
    )
}

function ChatPanel () {
    return (
        <Grid xs={12} md={8} sx={{
            paddingLeft: "1rem",
            paddingRight: "1rem",
        }}>
            <ChatPanelToolbar/>
            <ChatWindow/>
            <ChatInputBar/>
        </Grid>
    )
}

export default ChatPanel;