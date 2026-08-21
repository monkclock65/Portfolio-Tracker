import {useMutation} from '@tanstack/react-router'
import api from './api'


export default function useaddTransaction(transactionData) {
const addTransaction = useMutation({
    mutationFn: (transactionData) =>  api.post('/transaction/add-transaction')
})
}