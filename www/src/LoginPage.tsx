import {useState, useEffect} from 'react';
import Sheet from '@mui/joy/Sheet';
import Typography from '@mui/joy/Typography';
import Button from '@mui/joy/Button';
import type { StateProps, UserInfo } from './App';

type LoginUserInfo = {
    id: number,
    name: string,
    password: string,
    description: string,
    customer_segment: string,
    npl_status: string
}

function LoginUserSelect( props: {
    setState: React.Dispatch<React.SetStateAction<any>>,
    closePanelHandler: () => void
}){
    let [loginUsers, setLoginUsers] = useState<LoginUserInfo[]>([])

    useEffect(()=>{
        fetch('/api/users')
        .then(response => {
            return response.json()
        })
        .then(data => setLoginUsers(data.users))
        .catch((error) => {console.error('Error:', error)});
    },[])

    let loginHandler = (user: UserInfo )=>{
        props.closePanelHandler();
        props.setState({
            currentPage: "chat",
            currentUser: user,
            appState: "done"
        });        
    }

    let LoginUserList = loginUsers.map((user, index) => {
        return (
            <Sheet key={index} sx={{
                width: '30rem',
                margin: '1rem',
                padding: '1rem',
                borderRadius: '0.5rem',
                border: '0.1rem solid #78C1F3',
                ':hover': {
                    backgroundColor: '#E4F1FF',
                },
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'space-between',
            }}>
                <div>
                    <Typography level="h2" fontSize="xl" sx={{ mb: 0.5 }}>{user.name}</Typography>
                    <div>{user.description}</div>
                </div>
                <Button color="primary" onClick={() => loginHandler(user)}>เข้าสู่ระบบ</Button>
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
    let [openLoginList, setOpenLoginList] = useState(false);

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
            color="primary"
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