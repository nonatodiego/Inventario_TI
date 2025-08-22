import { useState, useEffect } from 'react'
import Login from '@/components/Login.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Users, Edit, Trash2, Search, Smartphone, Headphones, Monitor, BarChart3, Mouse, Keyboard, ChevronDown, ChevronUp } from 'lucide-react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, Legend } from 'recharts'
import './App.css'

function App() {
  const USE_BACKEND = true
  const [user, setUser] = useState(null)
  const [users, setUsers] = useState([])
  const [filteredUsers, setFilteredUsers] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSetor, setSelectedSetor] = useState('')
  const [selectedGestor, setSelectedGestor] = useState('')
  const [setores, setSetores] = useState([])
  const [gestores, setGestores] = useState([])
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showCharts, setShowCharts] = useState(false)
  const [isConfirmOpen, setIsConfirmOpen] = useState(false)
  const [userToDelete, setUserToDelete] = useState(null)
  const [formData, setFormData] = useState({
    nome_usuario: '',
    matricula: '',
    setor: '',
    nome_gestor: '',
    localizacao: '',
    desktop_notebook: '',
    segunda_tela: false,
    licenca_office: '',
    celular_corporativo: false,
    headset: false,
    mouse_sem_fio: false,
    teclado_sem_fio: false
  })

  // Carregar usuário autenticado e dados ao inicializar
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('auth_user')
      if (storedUser) {
        setUser(JSON.parse(storedUser))
      }
    } catch (_) {}
    setLoading(false)
    fetchUsers()
    fetchGestores()
  }, [])


  // Filtrar usuários
  useEffect(() => {
    let filtered = users
    
    if (searchTerm) {
      filtered = filtered.filter(user => 
        user.nome_usuario.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.matricula.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (user.setor && user.setor.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }
    
    if (selectedSetor) {
      filtered = filtered.filter(user => user.setor === selectedSetor)
    }
    
    if (selectedGestor) {
      filtered = filtered.filter(user => user.nome_gestor === selectedGestor)
    }
    
    setFilteredUsers(filtered)
  }, [users, searchTerm, selectedSetor, selectedGestor])

  // Atualizar lista de setores dinamicamente a partir dos usuários
  useEffect(() => {
    const uniqueSetores = Array.from(
      new Set(
        (users || [])
          .map(u => (u && typeof u.setor === 'string' ? u.setor.trim() : ''))
          .filter(s => s && s.length > 0)
      )
    ).sort((a, b) => a.localeCompare(b))
    setSetores(uniqueSetores)
  }, [users])



  const saveUsersToStorage = (list) => {
    try {
      localStorage.setItem('inventory_users', JSON.stringify(list))
    } catch (_) {}
    setUsers(list)
  }

  const fetchUsers = async () => {
    // Tenta carregar do backend primeiro
    if (USE_BACKEND) {
      try {
        const res = await fetch('/api/users')
        if (res.ok) {
          const data = await res.json()
          saveUsersToStorage(data)
          return
        }
      } catch (_) {}
    }

    // Tenta carregar do localStorage
    try {
      const stored = localStorage.getItem('inventory_users')
      if (stored) {
        setUsers(JSON.parse(stored))
        return
      }
    } catch (_) {}

    // Dados de exemplo para demonstração
    const mockUsers = [
      {
        id: 1,
        nome_usuario: 'João Silva',
        matricula: '12345',
        setor: 'TI',
        nome_gestor: 'Maria Santos',
        localizacao: 'São Paulo',
        desktop_notebook: 'Desktop',
        segunda_tela: true,
        licenca_office: 'O365 E3',
        assets: [{
          celular_corporativo: true,
          headset: true,
          mouse_sem_fio: false,
          teclado_sem_fio: true
        }]
      },
      {
        id: 2,
        nome_usuario: 'Ana Costa',
        matricula: '67890',
        setor: 'Financeiro',
        nome_gestor: 'Carlos Lima',
        localizacao: 'Rio de Janeiro',
        desktop_notebook: 'Notebook',
        segunda_tela: false,
        licenca_office: 'O365 E1',
        assets: [{
          celular_corporativo: false,
          headset: false,
          mouse_sem_fio: true,
          teclado_sem_fio: false
        }]
      },
      {
        id: 3,
        nome_usuario: 'Pedro Oliveira',
        matricula: '11111',
        setor: 'Vendas',
        nome_gestor: 'Lucia Ferreira',
        localizacao: 'Belo Horizonte',
        desktop_notebook: 'Notebook',
        segunda_tela: true,
        licenca_office: 'O365 E3',
        assets: [{
          celular_corporativo: true,
          headset: true,
          mouse_sem_fio: true,
          teclado_sem_fio: true
        }]
      }
    ]
    saveUsersToStorage(mockUsers)
  }

  // Removido: fetchSetores (setores agora são derivados de users)

  const fetchGestores = async () => {
    const mockGestores = ['Maria Santos', 'Carlos Lima', 'Lucia Ferreira', 'Roberto Silva', 'Ana Paula']
    setGestores(mockGestores)
  }

  const handleLogin = (loggedUser) => {
    setUser(loggedUser)
    try { localStorage.setItem('auth_user', JSON.stringify(loggedUser)) } catch (_) {}
  }

  const handleLogout = () => {
    try { localStorage.removeItem('auth_user') } catch (_) {}
    setUser(null)
  }

  // Toast simples (deve ficar antes de qualquer return condicional para manter a ordem dos hooks)
  const [toast, setToast] = useState({ visible: false, message: '', variant: 'success' })
  const showToast = (message, variant = 'success', timeout = 2500) => {
    setToast({ visible: true, message, variant })
    window.setTimeout(() => setToast({ visible: false, message: '', variant }), timeout)
  }
  const getToastClass = (variant) => {
    const base = 'fixed bottom-4 right-4 px-4 py-2 rounded-md text-white shadow-lg z-[9999]'
    const color = variant === 'destructive' ? 'bg-red-600' : (variant === 'secondary' ? 'bg-gray-800' : 'bg-green-600')
    return `${base} ${color}`
  }

  // Exibir tela de login quando não autenticado
  if (!user) {
    return <Login onLogin={handleLogin} />
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Se não estiver editando, criação está desativada
    if (!editingUser) {
      showToast('Criação de usuários está desativada', 'secondary')
      setIsDialogOpen(false)
      return
    }

    // Preferir backend quando habilitado
    if (USE_BACKEND) {
      try {
        if (editingUser) {
          const res = await fetch(`/api/users/${editingUser.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              nome_usuario: formData.nome_usuario,
              matricula: formData.matricula,
              setor: formData.setor,
              nome_gestor: formData.nome_gestor,
              localizacao: formData.localizacao,
              desktop_notebook: formData.desktop_notebook,
              segunda_tela: !!formData.segunda_tela,
              licenca_office: formData.licenca_office,
              celular_corporativo: !!formData.celular_corporativo,
              headset: !!formData.headset,
              mouse_sem_fio: !!formData.mouse_sem_fio,
              teclado_sem_fio: !!formData.teclado_sem_fio,
            })
          })
          if (!res.ok) throw new Error('Falha ao atualizar no backend')
        }
        // Recarregar lista do backend para refletir mudanças
        await fetchUsers()
        showToast('Usuário atualizado', 'success')
        setIsDialogOpen(false)
        resetForm()
        return
      } catch (err) {
        console.warn('Falha no backend, aplicando fallback local:', err)
      }
    }

    // Fallback local: comportamento anterior (localStorage)
    if (editingUser) {
      const updatedUsers = users.map(user => 
        user.id === editingUser.id 
          ? { ...user, ...formData, assets: [{ 
              celular_corporativo: formData.celular_corporativo,
              headset: formData.headset,
              mouse_sem_fio: formData.mouse_sem_fio,
              teclado_sem_fio: formData.teclado_sem_fio
            }] }
          : user
      )
      saveUsersToStorage(updatedUsers)
      showToast('Atualizado (modo local)', 'secondary')
    }
    setIsDialogOpen(false)
    resetForm()
  }

  const handleEdit = (user) => {
    setEditingUser(user)
    const assets = user.assets && user.assets.length > 0 ? user.assets[0] : {}
    setFormData({
      nome_usuario: user.nome_usuario || '',
      matricula: user.matricula || '',
      setor: user.setor || '',
      nome_gestor: user.nome_gestor || '',
      localizacao: user.localizacao || '',
      desktop_notebook: user.desktop_notebook || '',
      segunda_tela: user.segunda_tela || false,
      licenca_office: user.licenca_office || '',
      celular_corporativo: assets.celular_corporativo || false,
      headset: assets.headset || false,
      mouse_sem_fio: assets.mouse_sem_fio || false,
      teclado_sem_fio: assets.teclado_sem_fio || false
    })
    setIsDialogOpen(true)
  }

  const openConfirmDelete = (user) => {
    setUserToDelete(user)
    setIsConfirmOpen(true)
  }

  

  const handleDelete = async (userId) => {
    const targetId = String(userId)
    if (USE_BACKEND) {
      try {
        const res = await fetch(`/api/users/${targetId}`, { method: 'DELETE' })
        if (!res.ok) throw new Error('Falha ao excluir no backend')
        const updatedUsers = users.filter(user => String(user.id) !== targetId)
        saveUsersToStorage(updatedUsers)
        showToast('Usuário excluído com sucesso', 'success')
        return
      } catch (e) {
        // fallback local
      }
    }

    // Fallback local
    const updatedUsers = users.filter(user => String(user.id) !== targetId)
    saveUsersToStorage(updatedUsers)
    showToast('Usuário excluído (modo local)', 'secondary')
  }

  const resetForm = () => {
    setFormData({
      nome_usuario: '',
      matricula: '',
      setor: '',
      nome_gestor: '',
      localizacao: '',
      desktop_notebook: '',
      segunda_tela: false,
      licenca_office: '',
      celular_corporativo: false,
      headset: false,
      mouse_sem_fio: false,
      teclado_sem_fio: false
    })
    setEditingUser(null)
  }

  const openNewUserDialog = () => {
    resetForm()
    setIsDialogOpen(true)
  }

  const clearFilters = () => {
    setSearchTerm('')
    setSelectedSetor('')
    setSelectedGestor('')
  }


  // Removido: exportação em PDF

  const isAdmin = user && user.role === 'admin'

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Inventário de Ativos de TI</h1>
          <p>Carregando...</p>
        </div>
      </div>
    )
  }


  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Inventário de Ativos</h1>
              <p className="text-gray-600">Itracker T.I</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">{user?.username}</span>
              <Button variant="outline" onClick={handleLogout}>Sair</Button>
            </div>
          </div>
        </div>

        {/* Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <Users className="h-8 w-8 text-blue-600" />
                <div className="ml-4 text-center">
                  <p className="text-sm font-medium text-gray-600">Total de Usuários</p>
                  <p className="text-2xl font-bold text-gray-900">{users.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <Smartphone className="h-8 w-8 text-green-600" />
                <div className="ml-4 text-center">
                  <p className="text-sm font-medium text-gray-600">Celulares</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {users.filter(user => {
                      const assets = user.assets && user.assets.length > 0 ? user.assets[0] : {}
                      return assets.celular_corporativo
                    }).length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <Headphones className="h-8 w-8 text-purple-600" />
                <div className="ml-4 text-center">
                  <p className="text-sm font-medium text-gray-600">Headsets</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {users.filter(user => {
                      const assets = user.assets && user.assets.length > 0 ? user.assets[0] : {}
                      return assets.headset
                    }).length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <Monitor className="h-8 w-8 text-orange-600" />
                <div className="ml-4 text-center">
                  <p className="text-sm font-medium text-gray-600">Segunda Tela</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {users.filter(user => user.segunda_tela).length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Gráficos */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Gráficos
              </CardTitle>
              <Button 
                variant="outline" 
                onClick={() => setShowCharts(!showCharts)}
              >
                {showCharts ? (
                  <>
                    <ChevronUp className="h-4 w-4 mr-2" />
                    Esconder
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4 mr-2" />
                    Mostrar
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          {showCharts && (
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Gráfico de Tipos de Equipamento */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Desktop vs Notebook</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          {
                            name: 'Desktop',
                            value: users.filter(user => user.desktop_notebook === 'Desktop').length
                          },
                          {
                            name: 'Notebook',
                            value: users.filter(user => user.desktop_notebook === 'Notebook').length
                          },
                          {
                            name: 'Não informado',
                            value: users.filter(user => !user.desktop_notebook || user.desktop_notebook === '').length
                          }
                        ].filter(item => item.value > 0)}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {/* Desktop */}
                        <Cell fill="#3b82f6" />
                        {/* Notebook */}
                        <Cell fill="#f59e0b" />
                        {/* Não informado */}
                        <Cell fill="#94a3b8" />
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Gráfico de Licenças Office */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Licenças Office</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={[
                      {
                        name: 'O365 E1',
                        quantidade: users.filter(user => user.licenca_office === 'O365 E1').length
                      },
                      {
                        name: 'O365 E3',
                        quantidade: users.filter(user => user.licenca_office === 'O365 E3').length
                      },
                      {
                        name: 'Office 2019',
                        quantidade: users.filter(user => user.licenca_office === 'Office 2019').length
                      },
                      {
                        name: 'Sem licença',
                        quantidade: users.filter(user => !user.licenca_office || user.licenca_office === '').length
                      }
                    ].filter(item => item.quantidade > 0)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="quantidade">
                        {/* O365 E1 */}
                        <Cell fill="#3b82f6" />
                        {/* O365 E3 */}
                        <Cell fill="#f59e0b" />
                        {/* Office 2019 */}
                        <Cell fill="#2563eb" />
                        {/* Sem licença */}
                        <Cell fill="#f97316" />
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </CardContent>
          )}
        </Card>

        {/* Filtros e Busca */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="flex-1 max-w-xl">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Buscar por nome, matrícula ou setor..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 h-10"
                  />
                </div>
              </div>
              
              <div className="w-full lg:w-auto flex flex-wrap items-center justify-between lg:justify-start gap-3 mt-4 lg:mt-0 self-center p-6">
                <select
                  value={selectedSetor}
                  onChange={(e) => setSelectedSetor(e.target.value)}
                  className="h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 shrink-0"
                >
                  <option value="">Todos os setores</option>
                  {setores.map((setor) => (
                    <option key={setor} value={setor}>{setor}</option>
                  ))}
                </select>
                
                <select
                  value={selectedGestor}
                  onChange={(e) => setSelectedGestor(e.target.value)}
                  className="h-10 px-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 shrink-0"
                >
                  <option value="">Todos os gestores</option>
                  {gestores.map((gestor) => (
                    <option key={gestor} value={gestor}>{gestor}</option>
                  ))}
                </select>
                
                <Button variant="outline" className="h-10 shrink-0" onClick={clearFilters}>
                  Limpar Filtros
                </Button>
                
                {/* Criação de usuários desativada por requisito */}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Lista de Usuários */}
        <div className="space-y-4">
          {filteredUsers.map((user) => {
            const assets = user.assets && user.assets.length > 0 ? user.assets[0] : {}
            
            return (
              <Card key={user.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <Users className="h-5 w-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-gray-900">{user.nome_usuario}</h3>
                        <Badge variant="outline">{user.matricula}</Badge>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div>
                          <p className="text-sm text-gray-500">Setor</p>
                          <p className="font-medium">{user.setor || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Gestor</p>
                          <p className="font-medium">{user.nome_gestor || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Localização</p>
                          <p className="font-medium">{user.localizacao || 'N/A'}</p>
                        </div>
                      </div>
                      
                      <div className="flex flex-wrap gap-2">
                        {user.desktop_notebook && (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Monitor className="h-3 w-3" />
                            {user.desktop_notebook}
                          </Badge>
                        )}
                        {user.segunda_tela && (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Monitor className="h-3 w-3" />
                            Segunda Tela
                          </Badge>
                        )}
                        {assets.celular_corporativo && (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Smartphone className="h-3 w-3" />
                            Celular
                          </Badge>
                        )}
                        {assets.headset && (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Headphones className="h-3 w-3" />
                            Headset
                          </Badge>
                        )}
                        {assets.mouse_sem_fio && (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Mouse className="h-3 w-3" />
                            Mouse
                          </Badge>
                        )}
                        {assets.teclado_sem_fio && (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Keyboard className="h-3 w-3" />
                            Teclado
                          </Badge>
                        )}
                        {user.licenca_office && (
                          <Badge variant="outline">
                            {user.licenca_office}
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    {/* Controles de edição/exclusão desativados (somente leitura) */}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {filteredUsers.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum usuário encontrado</h3>
              <p className="text-gray-500">Tente ajustar os filtros ou adicione um novo usuário.</p>
            </CardContent>
          </Card>
        )}

        {/* Dialog para Novo/Editar Usuário - Apenas para Admins */}
        {isAdmin && (
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>
                  {editingUser ? 'Editar Usuário' : 'Novo Usuário'}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="nome_usuario">Nome do Usuário *</Label>
                    <Input
                      id="nome_usuario"
                      value={formData.nome_usuario}
                      onChange={(e) => setFormData({...formData, nome_usuario: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="matricula">Matrícula *</Label>
                    <Input
                      id="matricula"
                      value={formData.matricula}
                      onChange={(e) => setFormData({...formData, matricula: e.target.value})}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="setor">Setor</Label>
                    <Input
                      id="setor"
                      value={formData.setor}
                      onChange={(e) => setFormData({...formData, setor: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="nome_gestor">Nome do Gestor</Label>
                    <Input
                      id="nome_gestor"
                      value={formData.nome_gestor}
                      onChange={(e) => setFormData({...formData, nome_gestor: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="localizacao">Localização</Label>
                    <Input
                      id="localizacao"
                      value={formData.localizacao}
                      onChange={(e) => setFormData({...formData, localizacao: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="desktop_notebook">Desktop/Notebook</Label>
                    <select
                      id="desktop_notebook"
                      value={formData.desktop_notebook}
                      onChange={(e) => setFormData({...formData, desktop_notebook: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Selecione</option>
                      <option value="Desktop">Desktop</option>
                      <option value="Notebook">Notebook</option>
                    </select>
                  </div>
                  <div>
                    <Label htmlFor="licenca_office">Licença Office</Label>
                    <select
                      id="licenca_office"
                      value={formData.licenca_office}
                      onChange={(e) => setFormData({...formData, licenca_office: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Selecione</option>
                      <option value="O365 E1">O365 E1</option>
                      <option value="O365 E3">O365 E3</option>
                    </select>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <Label className="text-base font-medium">Equipamentos</Label>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="segunda_tela"
                        checked={formData.segunda_tela}
                        onCheckedChange={(checked) => setFormData({...formData, segunda_tela: checked})}
                      />
                      <Label htmlFor="segunda_tela">Segunda Tela</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="celular_corporativo"
                        checked={formData.celular_corporativo}
                        onCheckedChange={(checked) => setFormData({...formData, celular_corporativo: checked})}
                      />
                      <Label htmlFor="celular_corporativo">Celular Corporativo</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="headset"
                        checked={formData.headset}
                        onCheckedChange={(checked) => setFormData({...formData, headset: checked})}
                      />
                      <Label htmlFor="headset">Headset</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="mouse_sem_fio"
                        checked={formData.mouse_sem_fio}
                        onCheckedChange={(checked) => setFormData({...formData, mouse_sem_fio: checked})}
                      />
                      <Label htmlFor="mouse_sem_fio">Mouse sem Fio</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="teclado_sem_fio"
                        checked={formData.teclado_sem_fio}
                        onCheckedChange={(checked) => setFormData({...formData, teclado_sem_fio: checked})}
                      />
                      <Label htmlFor="teclado_sem_fio">Teclado sem Fio</Label>
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancelar
                  </Button>
                  <Button type="submit">
                    {editingUser ? 'Atualizar' : 'Criar'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        )}

        {/* Dialog de Confirmação de Exclusão */}
        <Dialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Confirmar exclusão</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <p>
                Tem certeza que deseja excluir o usuário{' '}
                <span className="font-semibold">{userToDelete?.nome_usuario}</span>?
                Esta ação não pode ser desfeita.
              </p>
              <div className="flex justify-end gap-2">
                <Button
                  variant="secondary"
                  onClick={() => { setIsConfirmOpen(false); setUserToDelete(null) }}
                >
                  Cancelar
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => { if (userToDelete) { handleDelete(userToDelete.id) }; setIsConfirmOpen(false); setUserToDelete(null) }}
                >
                  Excluir
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Toast */}
        {toast.visible && (
          <div className={getToastClass(toast.variant)}>
            {toast.message}
          </div>
        )}
      </div>
    </div>
  )
}

export default App

