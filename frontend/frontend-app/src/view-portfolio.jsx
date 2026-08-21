import {useMutation, useQuery} from '@tanstack/react-query'
import api from './api'

export default function ViewPortfolio() {
    const {portfolioid,isPending,isError,error}=useGetPortfolioid()

    if (isPending) {
        return <div className="portfolio-page"><div className="empty-state">loading...</div></div>
    }
    if (isError) {
        return <div className="portfolio-page"><div className="empty-state">Error: {error.message}</div></div>
    }
    if (!portfolioid) {
        return <div className="portfolio-page"><div className="empty-state">No portfolio found.</div></div>
    }

    return (
        <div className="portfolio-page">
            <div className="page-header">
                <div>
                    <p className="eyebrow">Portfolio overview</p>
                    <h1>Portfolio</h1>
                </div>
            </div>
            <AddTransaction portfolioid={portfolioid}/>
            <GetPortfolio portfolioid={portfolioid}/>
            <ReadTransactions portfolioid={portfolioid}/>
        </div>
    )
}

export function AddTransaction({portfolioid}) {
    const Transaction = useMutation({
        mutationFn: (transactionData) => api.post(`/transaction/add_transaction/${portfolioid}`,transactionData)
    })

    function handleAddTransaction(event) {
        event.preventDefault()
        const formData = new FormData(event.currentTarget)
        const type = formData.get('type')
        const shares = formData.get('shares')
        const price = formData.get('price')
        const transaction = {
            'type': type,
            'shares': shares,
            'price': price
        }
        Transaction.mutate(transaction)
    }

    return (
        <div className="panel add-transaction-panel">
            <div className="panel-header">
                <h2>Add transaction</h2>
            </div>
            <form className="transaction-form" onSubmit={handleAddTransaction}>
                <input name='type' placeholder='type' />
                <input name='shares' placeholder='shares' />
                <input name='price' placeholder='price' />
                <button type="submit" className="primary-button">
                    {Transaction.isPending ? 'adding transaction...' : 'add transaction'}
                </button>
            </form>
            {Transaction.isError ? (<div className="form-message error">an error occured: {Transaction.error.message}</div>) : null}
            {Transaction.isSuccess ? (<div className="form-message success">transaction added</div>) : null}
        </div>
    )
}

export function GetPortfolio({portfolioid}) {
    const {isError,isPending,error,data} = useQuery({
        queryKey: ['holdings',portfolioid],
        queryFn: () => api.get(`/holding/read_holdings/${portfolioid}`),
    })
    if (isPending) {
        return <div className="panel"><div className="empty-state">loading portfolio...</div></div>
    }
    if (isError) {
        return <div className="panel"><div className="empty-state">Error: {error.message}</div></div>
    }
    const holdings = data.data.holdings_summary
    const summary = data.data.portfolio_summary

    return (
        <div className="panel summary-panel">
            <div className="summary-grid">
                <div className="metric-card">
                    <span>Total Value</span>
                    <strong>{summary.total_value}</strong>
                </div>
                <div className="metric-card">
                    <span>Gain/Loss</span>
                    <strong>{summary.total_gain_loss}</strong>
                </div>
                <div className="metric-card">
                    <span>Gain/Loss %</span>
                    <strong>{summary.total_gain_loss_pct}</strong>
                </div>
            </div>

            <div className="holdings-list">
                {holdings.map((h) => {
                    return (
                        <div className="holding-row" key={h.symbol}>
                            <div className="holding-main">
                                <span className="ticker">{h.symbol}</span>
                                <span>{h.shares} shares @ {h.price}</span>
                            </div>
                            <div className="holding-meta">
                                <p>Value: {h.value}</p>
                                <p>Gain/Loss: {h.gain_loss}</p>
                                <p>Avg cost: {h.avg_cost_basis}</p>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

export function ReadTransactions({portfolioid}) {
    const {isError,isPending,error,data} = useQuery({
        queryKey: ['transactions',portfolioid],
        queryFn: () => api.get(`/transaction/read_all_transactions/${portfolioid}`)
    })
    if (isPending) {
        return <div className="panel"><div className="empty-state">loading transactions...</div></div>
    }
    if (isError) {
        return <div className="panel"><div className="empty-state">Error: {error.message}</div></div>
    }
    const transactions = data.data.transactions

    return (
        <div className="panel transactions-panel">
            <div className="panel-header">
                <h2>Transactions</h2>
            </div>
            <div className="transaction-list">
                {transactions.map((t)=> {
                    return (
                        <div className="transaction-row" key={t.id}>
                            <span className="ticker">{t.symbol}</span>
                            <span>{t.type}</span>
                            <span>{t.shares} shares</span>
                            <span>@ {t.price}</span>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

export function useGetPortfolioid() {
    const {isError,isPending,data,error} = useQuery({
        queryKey: ['portfolio'],
        queryFn: () => api.get('portfolio/read_portfolio')
    })

    return { portfolioid: data?.data[0]?.id, isPending, isError, error }
}