import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query'
import { useState } from 'react'
import api from './api'
import {Box, Card, CardContent, TableContainer, Table, TableHead, TableRow, TableCell, TableBody, Paper, Typography, TextField, Button, Stack, MenuItem } from '@mui/material'

function formatInteger(v) {
    const n = Number(v)
    if (!Number.isFinite(n)) return v
    return Math.round(n).toString()
}

function formatCurrency(v) {
    const n = Number(v)
    if (!Number.isFinite(n)) return v
    return `$${n.toFixed(2)}`
}

function formatPercent(v) {
    const n = Number(v)
    if (!Number.isFinite(n)) return v
    return `${n.toFixed(2)}%`
}

function formatNumber(v) {
    const n = Number(v)
    if (!Number.isFinite(n)) return v
    return n.toFixed(2)
}

function formatValueForKey(key, value) {
    const k = key.toLowerCase()
    if (k.includes('pct') || k.includes('percent')) return formatPercent(value)
    if (k.includes('value') || k.includes('price') || k.includes('cost') || k.includes('gain_loss') || k.includes('gain') || k.includes('loss')) return formatCurrency(value)
    return formatNumber(value)
}

export default function ViewPortfolio() {
    const {portfolioid,isPending,isError,error}=useGetPortfolioid()

    if (isPending) {
        return (
            <Box sx={{ p: 3 }}>
                <Card>
                    <CardContent>
                        <Typography variant="body1">Loading...</Typography>
                    </CardContent>
                </Card>
            </Box>
        )
    }

    if (isError && error?.response?.status !== 404) {
        return (
            <Box sx={{ p: 3 }}>
                <Card>
                    <CardContent>
                        <Typography color="error">Error: {error.message}</Typography>
                    </CardContent>
                </Card>
            </Box>
        )
    }

    if (!portfolioid) {
        return (
            <Box sx={{ p: { xs: 2, md: 3 }, backgroundColor: '#f3f9ff', minHeight: 'calc(100vh - 72px)' }}>
                <Box
                    sx={{
                        maxWidth: 1200,
                        mx: 'auto',
                        mb: 3,
                        px: { xs: 2, md: 3 },
                        py: 2.5,
                        borderRadius: 3,
                        background: 'linear-gradient(135deg, #0d47a1 0%, #1976d2 45%, #42a5f5 100%)',
                        color: 'white',
                        boxShadow: '0 12px 28px rgba(25, 118, 210, 0.2)'
                    }}
                >
                    <Typography variant="h3" component="h1" sx={{ fontWeight: 700, letterSpacing: '-0.04em' }}>
                        Portfolio
                    </Typography>
                </Box>
                <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" sx={{ mb: 2 }}>No portfolio yet</Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Create a portfolio from the app shell, or add your first transaction once a portfolio exists.
                            </Typography>
                        </CardContent>
                    </Card>
                </Box>
            </Box>
        )
    }

    return (
        <Box sx={{ p: { xs: 2, md: 3 }, backgroundColor: '#f3f9ff', minHeight: 'calc(100vh - 72px)' }}>
            <Box
                sx={{
                    maxWidth: 1200,
                    mx: 'auto',
                    mb: 3,
                    px: { xs: 2, md: 3 },
                    py: 2.5,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #0d47a1 0%, #1976d2 45%, #42a5f5 100%)',
                    color: 'white',
                    boxShadow: '0 12px 28px rgba(25, 118, 210, 0.2)'
                }}
            >
                <Typography variant="h3" component="h1" sx={{ fontWeight: 700, letterSpacing: '-0.04em' }}>
                    Portfolio
                </Typography>
            </Box>
            <GetPortfolio portfolioid={portfolioid} />
        </Box>
    )
}


export function AddTransaction({portfolioid}) {
    const queryClient = useQueryClient()
    const [transactionType, setTransactionType] = useState('BUY')
    const Transaction = useMutation({
        mutationFn: (transactionData) => api.post(`/transaction/add_transaction/${portfolioid}`, transactionData)
    })

    function handleAddTransaction(event) {
        event.preventDefault()
        const formData = new FormData(event.currentTarget)
        const symbol = String(formData.get('symbol') || '').trim().toUpperCase()
        const type = String(transactionType || '').toUpperCase()
        const shares = Number(formData.get('shares'))
        const rawPrice = formData.get('price')
        const price = rawPrice === '' || rawPrice === null ? undefined : Number(rawPrice)

        if (!symbol || !shares || Number.isNaN(shares) || shares <= 0) {
            return
        }

        if (type === 'BUY') {
            if (price === undefined || Number.isNaN(price) || price <= 0) {
                return
            }
        }

        const transaction = {
            symbol,
            transaction_type: type,
            shares,
            ...(type === 'BUY' ? { price } : {})
        }

        Transaction.mutate(transaction, {
            onSuccess: () => {
                queryClient.invalidateQueries(['holdings', portfolioid])
                queryClient.invalidateQueries(['transactions', portfolioid])
                queryClient.invalidateQueries(['portfolio'])
                event.currentTarget.reset()
                setTransactionType('BUY')
            }
        })
    }

    return (
        <Card sx={{ mb: 2 }}>
            <CardContent>
                <Typography variant="h6" sx={{ mb: 1 }}>Add transaction</Typography>
                <Box component="form" onSubmit={handleAddTransaction}>
                    <Stack direction="column" spacing={2} sx={{ alignItems: 'stretch' }}>
                        <TextField name='symbol' label='Symbol' placeholder='AAPL' size="small" fullWidth required />
                        <TextField
                            name='transaction_type'
                            label='Type'
                            select
                            size="small"
                            fullWidth
                            required
                            value={transactionType}
                            onChange={(event) => setTransactionType(event.target.value)}
                        >
                            <MenuItem value='BUY'>BUY</MenuItem>
                            <MenuItem value='SELL'>SELL</MenuItem>
                        </TextField>
                        <TextField
                            name='shares'
                            label='Shares'
                            placeholder='shares'
                            type='number'
                            slotProps={{ htmlInput: { step: 1, min: 0 } }}
                            size="small"
                            fullWidth
                            required
                        />
                        {transactionType === 'BUY' ? (
                            <TextField name='price' label='Price' placeholder='Enter price' type='number' size="small" fullWidth required />
                        ) : null}
                        <Button type="submit" variant="contained" color="primary" size="medium" fullWidth>
                            {Transaction.isLoading ? 'adding transaction...' : 'Add transaction'}
                        </Button>
                    </Stack>
                </Box>
                {Transaction.isError ? (<Typography color="error" sx={{ mt: 1 }}>an error occured: {Transaction.error.message}</Typography>) : null}
                {Transaction.isSuccess ? (<Typography color="success.main" sx={{ mt: 1 }}>transaction added</Typography>) : null}
            </CardContent>
        </Card>
    )
}

export function GetPortfolio({portfolioid}) {
    const {isError,isPending,error,data} = useQuery({
        queryKey: ['holdings',portfolioid],
        queryFn: () => api.get(`/holding/read_holdings/${portfolioid}`),
    })

    const {isError: txIsError, isPending: txIsPending, error: txError, data: txData} = useQuery({
        queryKey: ['transactions', portfolioid],
        queryFn: () => api.get(`/transaction/read_all_transactions/${portfolioid}`)
    })

    const holdings = data?.data?.holdings_summary || []
    const summary = data?.data?.portfolio_summary || {
        total_value: '0',
        total_cost_basis: '0',
        total_gain_loss: '0',
        total_gain_loss_pct: '0'
    }
    const transactions = txData?.data?.transactions || []

    const hasHoldings = holdings.length > 0
    const hasTransactions = transactions.length > 0

    if (isPending || txIsPending) {
        return <div className="panel"><div className="empty-state">loading portfolio...</div></div>
    }
    if (isError && error?.response?.status !== 404) {
        return <div className="panel"><div className="empty-state">Error: {error.message}</div></div>
    }
    if (txIsError && txError?.response?.status !== 404) {
        return <div className="panel"><div className="empty-state">Error: {txError.message}</div></div>
    }

    return (
        <Box sx={{ width: '100%', display: 'flex', justifyContent: 'center', p: 2, backgroundColor: '#f3f9ff' }}>
            <Box sx={{ width: '100%', maxWidth: 1200 }}>
                <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2, alignItems: 'stretch' }}>
                    <Box sx={{ width: { xs: '100%', md: '20%' } }}>
                        <AddTransaction portfolioid={portfolioid} />
                    </Box>

                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: { xs: '100%', md: '35%' } }}>
                        <Card sx={{ width: '100%' }}>
                            <CardContent>
                                <Typography variant="h6">Portfolio Summary</Typography>
                                <TableContainer component={Paper} sx={{ mt: 1 }}>
                                    <Table size="small">
                                        <TableBody>
                                            {Object.entries(summary).map(([key, value]) => (
                                                <TableRow key={key}>
                                                    <TableCell sx={{ textTransform: 'capitalize', width: 200 }}>{key.replace(/_/g, ' ')}</TableCell>
                                                    <TableCell>{formatValueForKey(key, value)}</TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </CardContent>
                        </Card>

                        <Card sx={{ width: '100%' }}>
                            <CardContent>
                                <Typography variant="h6">Transactions</Typography>
                                <TableContainer component={Paper} sx={{ mt: 1 }}>
                                    <Table size="small">
                                        <TableHead>
                                            <TableRow>
                                                <TableCell>Symbol</TableCell>
                                                <TableCell>Type</TableCell>
                                                <TableCell align="right">Shares</TableCell>
                                                <TableCell align="right">Price</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {hasTransactions ? (
                                                transactions.map((t) => (
                                                    <TableRow key={t.id}>
                                                        <TableCell>{t.symbol}</TableCell>
                                                        <TableCell>{t.type}</TableCell>
                                                        <TableCell align="right">{formatInteger(t.shares)}</TableCell>
                                                        <TableCell align="right">{formatCurrency(t.price)}</TableCell>
                                                    </TableRow>
                                                ))
                                            ) : (
                                                <TableRow>
                                                    <TableCell colSpan={4} sx={{ textAlign: 'center', color: 'text.secondary' }}>
                                                        No transactions yet
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </CardContent>
                        </Card>
                    </Box>

                    <Box sx={{ width: { xs: '100%', md: '45%' }, display: 'flex', flexDirection: 'column' }}>
                        <Card sx={{ width: '100%', display: 'flex', flexDirection: 'column', height: '100%' }}>
                            <CardContent sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                                <Typography variant="h6">Holdings</Typography>
                                <TableContainer component={Paper} sx={{ mt: 1, flex: 1, overflow: 'auto' }}>
                                    <Table sx={{ width: '100%' }}>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell>Symbol</TableCell>
                                                <TableCell align="right">Shares</TableCell>
                                                <TableCell align="right">Price</TableCell>
                                                <TableCell align="right">Value</TableCell>
                                                <TableCell align="right">Gain/Loss</TableCell>
                                                <TableCell align="right">Avg Cost</TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {hasHoldings ? (
                                                holdings.map((h) => (
                                                    <TableRow key={h.symbol}>
                                                        <TableCell>{h.symbol}</TableCell>
                                                        <TableCell align="right">{formatInteger(h.shares)}</TableCell>
                                                        <TableCell align="right">{formatCurrency(h.price)}</TableCell>
                                                        <TableCell align="right">{formatCurrency(h.value)}</TableCell>
                                                        <TableCell align="right">{formatCurrency(h.gain_loss)}</TableCell>
                                                        <TableCell align="right">{formatCurrency(h.avg_cost_basis)}</TableCell>
                                                    </TableRow>
                                                ))
                                            ) : (
                                                <TableRow>
                                                    <TableCell colSpan={6} sx={{ textAlign: 'center', color: 'text.secondary' }}>
                                                        No holdings yet
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </CardContent>
                        </Card>
                    </Box>
                </Box>
            </Box>
        </Box>
    )
}


export function useGetPortfolioid() {
    const {isError,isPending,data,error} = useQuery({
        queryKey: ['portfolio'],
        queryFn: () => api.get('portfolio/read_portfolio')
    })

    return { portfolioid: data?.data?.[0]?.id ?? null, isPending, isError, error }
}