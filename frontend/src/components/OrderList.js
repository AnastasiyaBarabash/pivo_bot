import React, { useEffect, useState, useRef } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Button,
    Paper,
} from '@mui/material';
import axios from 'axios';
import io from 'socket.io-client';

const OrderList = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const socketRef = useRef(null);

    const fetchOrders = async () => {
        try {
            const response = await axios.get('/api/orders/');
            setOrders(response.data);
        } catch (error) {
            console.error('Ошибка при получении заказов:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();

        socketRef.current = io(window.location.origin, { path: '/socket.io' });

        socketRef.current.on('new_order', (newOrder) => {
            setOrders((prevOrders) =>
                [newOrder, ...prevOrders].sort(
                    (a, b) => new Date(b.created_at) - new Date(a.created_at)
                )
            );
        });

        socketRef.current.on('order_status_updated', (updatedOrder) => {
            setOrders((prevOrders) =>
                prevOrders.map((order) =>
                    order.id === updatedOrder.id
                        ? { ...order, status: updatedOrder.status }
                        : order
                )
            );
        });

        return () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
            }
        };
    }, []);

    const handleStatusChange = async (orderId, newStatus) => {
        try {
            await axios.patch(`/api/orders/${orderId}/`, { status: newStatus });
            fetchOrders();
        } catch (error) {
            console.error('Ошибка при обновлении статуса заказа:', error);
        }
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Имя пользователя</TableCell>
                        <TableCell>Название напитка</TableCell>
                        <TableCell>Статус</TableCell>
                        <TableCell>Действия</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {orders
                        .sort(
                            (a, b) =>
                                new Date(b.created_at) - new Date(a.created_at)
                        )
                        .map((order) => (
                            <TableRow key={order.id}>
                                <TableCell>{order.username}</TableCell>
                                <TableCell>{order.drink_name}</TableCell>
                                <TableCell>{order.status}</TableCell>
                                <TableCell>
                                    <Button
                                        variant="contained"
                                        color="success"
                                        onClick={() =>
                                            handleStatusChange(
                                                order.id,
                                                'в работе'
                                            )
                                        }
                                    >
                                        В работе
                                    </Button>
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        onClick={() =>
                                            handleStatusChange(
                                                order.id,
                                                'готово'
                                            )
                                        }
                                    >
                                        Готово
                                    </Button>
                                    <Button
                                        variant="contained"
                                        color="error"
                                        onClick={() =>
                                            handleStatusChange(
                                                order.id,
                                                'отменено'
                                            )
                                        }
                                    >
                                        Отменено
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default OrderList;
