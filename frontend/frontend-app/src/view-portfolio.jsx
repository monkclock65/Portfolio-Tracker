import {useMutation, useQuery} from '@tanstack/react-query'
import api from './api'
export default function ViewPortfolio() {
    const {portfolioid,isPending,isError}=useGetPortfolioid()
    return (<div>
            <AddTransaction portfolioid={portfolioid}/>
            <GetPortfolio portfolioid={portfolioid}/>
            <ReadTransactions portfolioid={portfolioid}/>
                </div>
            )
}



export function AddTransaction({portfolioid}) {
const Transaction = useMutation({
    mutationFn: (transactionData) => api.post(`/transaction/add-transaction/${portfolioid}`,transactionData)

})
function handleAddTransaction(formData) {
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
   <div>
    <form action={handleAddTransaction}>
        <input name= 'type'/> //turn into dropdown later
        <input name= 'shares'/>
        <input name= 'price'/> 

    </form>
    {Transaction.isError ? (<div>an error occured: {Transaction.error.message}</div>):null}
    {Transaction.isPending ? ('adding transaction...'):null}
    {Transaction.isSuccess ? ('transaction added'):null}
   </div> 
)
}

export function GetPortfolio({portfolioid}) {
    const {isError,isPending,error} = useQuery({
        queryKey: ['holdings',portfolioid],
        queryFn: () => api.get(`/holding/read_holdings/${portfolioid}`),
    })
    if (isPending) {
        return <span>loading...</span>
    }
    if (isError) {
        return <span>Error: {error.message} </span>
    }
    return (
        <div>
            //figure out how to format later
        </div>
    )
}

export function ReadTransactions({portfolioid}) {
    const {isError,isPending,error} = useQuery({
        queryKey: ['transactions',portfolioid],
        queryFn: () => api.get(`/transaction/read-all-transactions/${portfolioid}`)
    })
     if (isPending) {
        return <span>loading...</span>
    }
    if (isError) {
        return <span>Error: {error.message} </span>
    }
    return (
        <div>
            //figure out how to format later
        </div>
    )
}

export function useGetPortfolioid() {
    const {isError,isPending,data} = useQuery({
        queryKey: ['portfolio'],
        queryFn: () => api.get('portfolio/read_portfolio')
    })
    
    return { portfolioid: data?.data[0]?.id, isPending, isError };
}