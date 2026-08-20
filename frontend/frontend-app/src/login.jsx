import {
  useMutation
} from '@tanstack/react-query'
import  api from './api'
import {useState} from 'react'

 export default function Login() {
    const [error,setError] = useState('')
    const loginMutation = useMutation({

        mutationFn: (loginData) => api.post('/auth/login', loginData),
        
        onSuccess: (response) => { localStorage.setItem('access_token', response.data.access_token) }
    
        })
    
    function handleLogin(formData) {
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
                <form action={handleLogin}>
                <input name='username'/>
                <input name='password'/>
                <button type="submit">{loginMutation.isPending ? <div>logging in...</div> : null}login</button>
            </form>
            {loginMutation.isError ? (loginMutation.error.message):null}
            <div>{error}</div>
            <div></div>
        </div>
    )

}

    
    




