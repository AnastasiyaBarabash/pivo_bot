import React from 'react';
import OrderList from './components/OrderList';
import { Container, Typography } from '@mui/material';

function App() {
    return (
        <Container>
            <Typography variant="h4" gutterBottom>
                Панель бармена
            </Typography>
            <OrderList />
        </Container>
    );
}

export default App;
