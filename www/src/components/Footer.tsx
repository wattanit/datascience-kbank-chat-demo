import Sheet from '@mui/joy/Sheet';

function Footer () {
    return (
        <Sheet sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'absolute',
            bottom: 0,
            width: '100%',        
        }}>
            <p>© 2024 TN Digital Solutions</p>
        </Sheet>
    )
}

export default Footer;