import {
  useMutation
} from '@tanstack/react-query'
import  api from './api'
import {useState} from 'react'
import {useNavigate} from 'react-router-dom'

 export default function Login() {
    const navigate = useNavigate()
    const [error,setError] = useState('')
    const loginMutation = useMutation({

        mutationFn: (loginData) => api.post('/auth/login', loginData),
        
        onSuccess: (response) => {
            localStorage.setItem('access_token', response.data.access_token)
            navigate('/portfolio')
        }
    
        })
    
    function handleLogin(event) {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    const username = formData.get('username')
    const password = formData.get('password')
    if (!password || !username) {
        setError('password or username field empty')
        return
        }
        setError('')
    loginMutation.mutate({username, password});
    }

    return (
        <div>
                <form onSubmit={handleLogin}>
                <input name='username'/>
                <input name='password'/>
                <button type="submit">{loginMutation.isPending ? 'logging in...' : 'login'}</button>
            </form>
            {loginMutation.isError ? (loginMutation.error.message):null}
            <div>{error}</div>
            <div></div>
        </div>
    )

}

