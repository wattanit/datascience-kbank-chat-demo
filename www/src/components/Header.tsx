import Sheet from '@mui/joy/Sheet';

function Header() {
    return (
        <Sheet
            variant="solid"
            color='neutral'
            sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                margin: '0 0 0.5rem 0',
                padding: '0 1rem',
                backgroundColor: '#59c8dd',
            }}
            >
            <h3>Credit Card Chat Assistant</h3>
        </Sheet>
    );
}

export default Header;