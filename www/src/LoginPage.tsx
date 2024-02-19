import React from 'react';
import Sheet from '@mui/joy/Sheet';
import Typography from '@mui/joy/Typography';
import Button from '@mui/joy/Button';
import { Menu, MenuButton } from '@mui/joy';

function LoginPanel () {
    let [openLoginList, setOpenLoginList] = React.useState(false);

    let LoginUsers = [
        {name: "JohnDoe", password: "password1", description: "คนธรรมดา"},
        {name: "สาริกา ลิ้นวัว", password: "password2", description: "คุณนายเจ้าของตลาด"},
        {name: "ทาย หนูน้ำ", password: "password3", description: "วัยรุ่นสร้างตัว"},
    ]

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
                }
            }}>
                <Typography level="h2" fontSize="xl" sx={{ mb: 0.5 }}>{user.name}</Typography>
                <div>{user.description}</div>
            </Sheet>
        )
    });

    let renderUserList = (openLoginList) ? LoginUserList : null;

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
            onClick={() => setOpenLoginList(!openLoginList)}
            color="success"
            size="lg">
            โปรดเลือกลูกค้าที่ต้องการเข้าสู่ระบบ
        </Button>
        {renderUserList}
      </Sheet>
    )
  }

function LoginPage (){
    return (
        <div>
            <LoginPanel/>
        </div>
    )
}

export default LoginPage;