import React from 'react';
import Sheet from '@mui/joy/Sheet';
import Typography from '@mui/joy/Typography';
import Button from '@mui/joy/Button';
import type { StateProps, UserInfo } from './App';

function LoginUserSelect( props: {
    setState: React.Dispatch<React.SetStateAction<any>>,
    closePanelHandler: () => void
}){
    let LoginUsers = [
        {id: 1, name: "JohnDoe", password: "password1", description: "คนธรรมดา"},
        {id: 2, name: "สาริกา ลิ้นวัว", password: "password2", description: "คุณนายเจ้าของตลาด"},
        {id: 3, name: "ทาย หนูน้ำ", password: "password3", description: "วัยรุ่นสร้างตัว"},
    ]

    let loginHandler = (user: UserInfo )=>{
        props.closePanelHandler();
        props.setState({
            currentPage: "chat",
            currentUser: user
        });        
    }

    let LoginUserList = LoginUsers.map((user, index) => {
        return (
            <Sheet key={index} sx={{
                width: '30rem',
                margin: '1rem',
                padding: '1rem',
                borderRadius: '0.5rem',
                border: '0.1rem solid rgba(1,200,50, 0.5)',
                ':hover': {
                    backgroundColor: 'rgba(1,200,50, 0.1)',
                },
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'space-between',
            }}>
                <div>
                    <Typography level="h2" fontSize="xl" sx={{ mb: 0.5 }}>{user.name}</Typography>
                    <div>{user.description}</div>
                </div>
                <Button color="success" onClick={() => loginHandler(user)}>เข้าสู่ระบบ</Button>
            </Sheet>
        )
    });

    return (
        <Sheet sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            overflowY: "auto",
            position: "fixed",
            zIndex: 1,
            left: "20vw",
            top: "10vh",
            width: "60vw",
            height: "75vh",
            overflow: "auto",
            border: "1px solid #ddd",
            backgroundColor: "rgba(255,255,255,0.9)",
        }}>
            {LoginUserList}
            <Button color='neutral' onClick={props.closePanelHandler}>Close</Button>
        </Sheet>
    )
}

function LoginPanel ( props: StateProps) {
    let [openLoginList, setOpenLoginList] = React.useState(false);

    let renderUserList = (openLoginList) ? <LoginUserSelect setState={props.setState} closePanelHandler={()=>{setOpenLoginList(false)}}/> : null;

    return (
      <Sheet
        variant="plain"
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1rem',
          margin: '1rem',
          height: '75vh',
        }}
      >
        <h2>Login</h2>
        <Button
            onClick={() => setOpenLoginList(true)}
            color="success"
            size="lg">
            โปรดเลือกลูกค้าที่ต้องการเข้าสู่ระบบ
        </Button>
        {renderUserList}
      </Sheet>
    )
  }

function LoginPage (props: StateProps){
    return (
        <div>
            <LoginPanel {...props}/>
        </div>
    )
}

export default LoginPage;