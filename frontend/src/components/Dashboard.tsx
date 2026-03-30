import React, { useState, useEffect, useCallback } from 'react';
import { Radio, MapPin, Battery, Wifi, CheckCircle2, AlertCircle, Clock, Map as MapIcon, Plus, X, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { coordinationApi } from '@/api/coordinationApi';
import { monitoringApi } from '@/api/monitoringApi';
import type { AgentStatus, Mission, MissionCreate, Assignment } from '@/api/types';

interface FAQItem {
  question: string;
  answer: string;
}

const faqItems: FAQItem[] = [
  {
    question: 'Как создаётся поисковая миссия?',
    answer: 'Внешний клиент или операторская система отправляет запрос в микросервис координации с описанием происшествия. Сервис автоматически формирует набор задач, выделяет сектора обследования и назначает доступных агентов на зоны поиска.'
  },
  {
    question: 'Как определяется доступность агентов?',
    answer: 'Микросервис координации запрашивает у микросервиса мониторинга актуальную информацию о каждом устройстве: уровень заряда батареи, качество связи и текущий статус. Только агенты с достаточным зарядом и стабильной связью назначаются на миссию.'
  },
  {
    question: 'Что происходит при потере связи с агентом?',
    answer: 'При потере связи система автоматически перераспределяет задачи на другие доступные устройства. Сектор, закреплённый за недоступным агентом, передаётся ближайшему свободному роботу с достаточным уровнем заряда.'
  },
  {
    question: 'Как отслеживается прогресс выполнения миссии?',
    answer: 'Каждый агент передаёт статусы выполнения задач в реальном времени. Микросервис координации агрегирует данные от всех участников миссии и предоставляет общую картину прогресса через операторский интерфейс.'
  },
  {
    question: 'Можно ли изменить параметры миссии во время выполнения?',
    answer: 'Да, оператор может в любой момент перераспределить сектора, добавить или исключить агентов, изменить приоритеты задач. Все изменения мгновенно передаются активным устройствам через микросервис координации.'
  },
  {
    question: 'Как система обрабатывает критически низкий заряд агента?',
    answer: 'При достижении критического уровня заряда (обычно 20%) агент автоматически возвращается на базу для подзарядки. Его задачи перераспределяются, а в интерфейсе отображается уведомление о необходимости замены или ожидания зарядки.'
  }
];

// ── helper functions ──────────────────────────────────────────────────────────

function getMissionStatusColor(status: Mission['status']): string {
  switch (status) {
    case 'IN_PROGRESS': return 'bg-blue-500';
    case 'COMPLETED': return 'bg-green-500';
    case 'CREATED':
    case 'PLANNING': return 'bg-yellow-500';
    case 'CANCELLED': return 'bg-red-500';
    default: return 'bg-gray-500';
  }
}

function getMissionStatusText(status: Mission['status']): string {
  switch (status) {
    case 'IN_PROGRESS': return 'Выполняется';
    case 'COMPLETED': return 'Завершена';
    case 'CREATED': return 'Создана';
    case 'PLANNING': return 'Планирование';
    case 'CANCELLED': return 'Отменена';
    default: return 'Неизвестно';
  }
}

function getAgentHealthColor(state: AgentStatus['health_state']): string {
  switch (state) {
    case 'HEALTHY': return 'bg-green-500';
    case 'WARNING': return 'bg-yellow-500';
    case 'CRITICAL': return 'bg-orange-500';
    case 'OFFLINE': return 'bg-red-500';
    default: return 'bg-gray-500';
  }
}

function getAgentHealthText(state: AgentStatus['health_state']): string {
  switch (state) {
    case 'HEALTHY': return 'Активен';
    case 'WARNING': return 'Предупреждение';
    case 'CRITICAL': return 'Критично';
    case 'OFFLINE': return 'Офлайн';
    default: return 'Неизвестно';
  }
}

function getBatteryColor(battery: number): string {
  if (battery > 60) return 'text-green-500';
  if (battery > 30) return 'text-yellow-500';
  return 'text-red-500';
}

function getLinkColor(link: AgentStatus['link_status']): string {
  switch (link) {
    case 'ONLINE': return 'text-green-500';
    case 'DEGRADED': return 'text-yellow-500';
    case 'OFFLINE': return 'text-red-500';
    default: return 'text-gray-500';
  }
}

function getPriorityColor(priority: Mission['priority']): string {
  switch (priority) {
    case 'LOW': return 'text-gray-500';
    case 'MEDIUM': return 'text-yellow-500';
    case 'HIGH': return 'text-orange-500';
    case 'CRITICAL': return 'text-red-500';
    default: return 'text-gray-500';
  }
}

function getPriorityText(priority: Mission['priority']): string {
  switch (priority) {
    case 'LOW': return 'Низкий';
    case 'MEDIUM': return 'Средний';
    case 'HIGH': return 'Высокий';
    case 'CRITICAL': return 'Критический';
    default: return priority;
  }
}

// ── component ─────────────────────────────────────────────────────────────────

const SearchCoordinationDashboard: React.FC = () => {
  const [view, setView] = useState<'dashboard' | 'map'>('dashboard');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  // ── API state ─────────────────────────────────────────────────────────────
  const [missions, setMissions] = useState<Mission[]>([]);
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [missionAssignments, setMissionAssignments] = useState<Record<number, Assignment[]>>({});
  const [loadingMissions, setLoadingMissions] = useState(true);
  const [loadingAgents, setLoadingAgents] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    try {
      const data = await monitoringApi.getAvailableAgents();
      setAgents(data);
    } catch (e) {
      setApiError((e as Error).message);
    } finally {
      setLoadingAgents(false);
    }
  }, []);

  const fetchMissions = useCallback(async () => {
    setLoadingMissions(true);
    try {
      const results = await Promise.allSettled(
        Array.from({ length: 20 }, (_, i) => coordinationApi.getMission(i + 1))
      );
      const found: Mission[] = [];
      for (const r of results) {
        if (r.status === 'fulfilled') found.push(r.value);
      }
      setMissions(found);
      const assignmentResults = await Promise.allSettled(
        found.map(m => coordinationApi.getAssignments(m.id))
      );
      const byMission: Record<number, Assignment[]> = {};
      assignmentResults.forEach((r, i) => {
        if (r.status === 'fulfilled') byMission[found[i].id] = r.value;
      });
      setMissionAssignments(byMission);
    } catch (e) {
      setApiError((e as Error).message);
    } finally {
      setLoadingMissions(false);
    }
  }, []);

  useEffect(() => {
    fetchMissions();
    fetchAgents();
  }, [fetchMissions, fetchAgents]);

  // poll agents every 10 s
  useEffect(() => {
    const id = setInterval(fetchAgents, 10_000);
    return () => clearInterval(id);
  }, [fetchAgents]);

  // ── Create mission form ───────────────────────────────────────────────────
  type IncidentType = 'BUILDING_COLLAPSE' | 'FIRE' | 'INDUSTRIAL_ACCIDENT' | 'FLOOD' | 'OTHER';
  const emptyForm = (): {
    incident_type: IncidentType;
    location: string;
    description: string;
    priority: MissionCreate['priority'];
    required_agents: number;
    centerLat: number;
    centerLng: number;
  } => ({
    incident_type: 'OTHER',
    location: '',
    description: '',
    priority: 'MEDIUM',
    required_agents: 2,
    centerLat: 55.7558,
    centerLng: 37.6173,
  });

  const [newMission, setNewMission] = useState(emptyForm);
  const [creating, setCreating] = useState(false);
  const [sectorToAdd, setSectorToAdd] = useState<{
    type: 'forest' | 'urban' | 'industrial' | 'water' | 'mountain';
    name: string;
  }>({ type: 'forest', name: '' });
  const [dialogSectors, setDialogSectors] = useState<Array<{
    id: string;
    name: string;
    type: typeof sectorToAdd.type;
  }>>([]);

  const handleAddSector = () => {
    if (!sectorToAdd.name.trim()) return;
    setDialogSectors(prev => [...prev, { id: `S-${Date.now()}`, ...sectorToAdd }]);
    setSectorToAdd({ type: 'forest', name: '' });
  };

  const handleRemoveSector = (id: string) => {
    setDialogSectors(prev => prev.filter(s => s.id !== id));
  };

  const handleCreateMission = async () => {
    if (!newMission.location.trim()) return;
    setCreating(true);
    try {
      const created = await coordinationApi.createMission({
        incident_type: newMission.incident_type,
        location: newMission.location,
        priority: newMission.priority,
        required_agents: newMission.required_agents,
      });
      await coordinationApi.planMission(created.id);
      await fetchMissions();
      setIsCreateDialogOpen(false);
      setNewMission(emptyForm());
      setDialogSectors([]);
    } catch (e) {
      setApiError((e as Error).message);
    } finally {
      setCreating(false);
    }
  };

  // ── derived stats ─────────────────────────────────────────────────────────
  const activeMissions = missions.filter(m => m.status === 'IN_PROGRESS');
  const availableAgents = agents.filter(a => a.health_state !== 'OFFLINE');
  const completedMissions = missions.filter(m => m.status === 'COMPLETED');
  const activeSectors = activeMissions.reduce((acc, m) => {
    const assignments = missionAssignments[m.id] ?? [];
    return acc + assignments.length;
  }, 0);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-foreground">
                Система координации поисковых миссий
              </h1>
              <p className="text-muted-foreground text-lg">
                Управление роботизированными агентами и распределение задач в реальном времени
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={() => { fetchMissions(); fetchAgents(); }}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Обновить
              </Button>
              <div className="flex items-center gap-2 bg-accent rounded-lg p-1">
                <Button
                  variant={view === 'dashboard' ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setView('dashboard')}
                >
                  <Radio className="w-4 h-4 mr-2" />
                  Дашборд
                </Button>
                <Button
                  variant={view === 'map' ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setView('map')}
                >
                  <MapIcon className="w-4 h-4 mr-2" />
                  Карта
                </Button>
              </div>

              {/* Create mission dialog */}
              <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Создать миссию
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Создание новой миссии</DialogTitle>
                    <DialogDescription>Заполните параметры поисковой операции</DialogDescription>
                  </DialogHeader>
                  <div className="space-y-6 py-4">
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="incident_type">Тип происшествия</Label>
                        <Select
                          value={newMission.incident_type}
                          onValueChange={v => setNewMission({ ...newMission, incident_type: v as IncidentType })}
                        >
                          <SelectTrigger id="incident_type">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="BUILDING_COLLAPSE">🏗️ T обрушение здания</SelectItem>
                            <SelectItem value="FIRE">🔥 Пожар</SelectItem>
                            <SelectItem value="INDUSTRIAL_ACCIDENT">🏭 Промавария</SelectItem>
                            <SelectItem value="FLOOD">🌊 Наводнение</SelectItem>
                            <SelectItem value="OTHER">🔍 Другое</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="location">Местоположение</Label>
                        <Input
                          id="location"
                          placeholder="Лесной массив, северный квадрат"
                          value={newMission.location}
                          onChange={e => setNewMission({ ...newMission, location: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="description">Описание (необязательно)</Label>
                        <Textarea
                          id="description"
                          placeholder="Подробное описание происшествия и зоны поиска"
                          value={newMission.description}
                          onChange={e => setNewMission({ ...newMission, description: e.target.value })}
                          rows={3}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="priority">Приоритет</Label>
                          <Select
                            value={newMission.priority}
                            onValueChange={v => setNewMission({ ...newMission, priority: v as MissionCreate['priority'] })}
                          >
                            <SelectTrigger id="priority">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="LOW">Низкий</SelectItem>
                              <SelectItem value="MEDIUM">Средний</SelectItem>
                              <SelectItem value="HIGH">Высокий</SelectItem>
                              <SelectItem value="CRITICAL">Критический</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="required_agents">Кол-во агентов</Label>
                          <Input
                            id="required_agents"
                            type="number"
                            min="1"
                            max="10"
                            value={newMission.required_agents}
                            onChange={e => setNewMission({ ...newMission, required_agents: parseInt(e.target.value) || 1 })}
                          />
                        </div>
                      </div>
                    </div>

                    <div className="border-t pt-4 space-y-4">
                      <div>
                        <h3 className="font-semibold mb-3">Центр зоны поиска</h3>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="centerLat">Широта</Label>
                            <Input
                              id="centerLat"
                              type="number"
                              step="0.0001"
                              value={newMission.centerLat}
                              onChange={e => setNewMission({ ...newMission, centerLat: parseFloat(e.target.value) || 0 })}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="centerLng">Долгота</Label>
                            <Input
                              id="centerLng"
                              type="number"
                              step="0.0001"
                              value={newMission.centerLng}
                              onChange={e => setNewMission({ ...newMission, centerLng: parseFloat(e.target.value) || 0 })}
                            />
                          </div>
                        </div>
                      </div>

                      <div className="h-48 bg-accent/20 rounded-lg border overflow-hidden">
                        <iframe
                          width="100%"
                          height="100%"
                          style={{ border: 0 }}
                          src={`https://www.openstreetmap.org/export/embed.html?bbox=${newMission.centerLng - 0.05},${newMission.centerLat - 0.05},${newMission.centerLng + 0.05},${newMission.centerLat + 0.05}&layer=mapnik&marker=${newMission.centerLat},${newMission.centerLng}`}
                          title="Карта центра поиска"
                        />
                      </div>
                    </div>

                    <div className="border-t pt-4 space-y-4">
                      <div>
                        <h3 className="font-semibold mb-3">Дополнительные секторы (для описания)</h3>
                        <div className="space-y-3">
                          <div className="flex gap-2">
                            <div className="flex-1">
                              <Input
                                placeholder="Название сектора"
                                value={sectorToAdd.name}
                                onChange={e => setSectorToAdd({ ...sectorToAdd, name: e.target.value })}
                              />
                            </div>
                            <Select
                              value={sectorToAdd.type}
                              onValueChange={v => setSectorToAdd({ ...sectorToAdd, type: v as typeof sectorToAdd.type })}
                            >
                              <SelectTrigger className="w-[150px]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="forest">🌲 Лес</SelectItem>
                                <SelectItem value="urban">🏙️ Город</SelectItem>
                                <SelectItem value="industrial">🏭 Промзона</SelectItem>
                                <SelectItem value="water">💧 Водоём</SelectItem>
                                <SelectItem value="mountain">⛰️ Горы</SelectItem>
                              </SelectContent>
                            </Select>
                            <Button onClick={handleAddSector} size="icon" type="button">
                              <Plus className="w-4 h-4" />
                            </Button>
                          </div>
                          {dialogSectors.length > 0 ? (
                            <div className="space-y-2 max-h-40 overflow-y-auto">
                              {dialogSectors.map(sector => (
                                <div key={sector.id} className="flex items-center justify-between p-2 border rounded-lg bg-accent/30">
                                  <div className="font-medium text-sm">{sector.name} — {sector.type}</div>
                                  <Button size="icon" variant="ghost" onClick={() => handleRemoveSector(sector.id)}>
                                    <X className="w-4 h-4" />
                                  </Button>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="text-center py-6 text-muted-foreground text-sm border-2 border-dashed rounded-lg">
                              Секторы не добавлены
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  {apiError && (
                    <p className="text-sm text-red-500 px-1 pb-2">{apiError}</p>
                  )}
                  <div className="flex justify-end gap-3">
                    <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>Отмена</Button>
                    <Button onClick={handleCreateMission} disabled={creating || !newMission.location.trim()}>
                      {creating ? 'Создание...' : 'Создать миссию'}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>

        {/* Error banner */}
        {apiError && !isCreateDialogOpen && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 flex items-center justify-between">
            <span>Ошибка API: {apiError}</span>
            <Button variant="ghost" size="sm" onClick={() => setApiError(null)}><X className="w-4 h-4" /></Button>
          </div>
        )}

        {/* Map view */}
        {view === 'map' && (
          <Card className="h-[600px]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapIcon className="w-5 h-5" />
                Карта поисковых зон
              </CardTitle>
              <CardDescription>Визуализация секторов обследования и позиций агентов</CardDescription>
            </CardHeader>
            <CardContent className="h-[500px]">
              <div className="w-full h-full rounded-lg border overflow-hidden relative">
                <iframe
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  src="https://www.openstreetmap.org/export/embed.html?bbox=37.5173,55.6558,37.7173,55.8558&layer=mapnik&marker=55.7558,37.6173"
                  className="rounded-lg"
                  title="Карта поисковых зон"
                />
                <div className="absolute top-4 left-4 bg-background/95 backdrop-blur-sm rounded-lg p-3 shadow-lg max-w-xs">
                  <h4 className="font-semibold text-sm mb-2">Активные миссии</h4>
                  <div className="space-y-2">
                    {activeMissions.length === 0 ? (
                      <p className="text-xs text-muted-foreground">Нет активных миссий</p>
                    ) : activeMissions.map(m => (
                      <div key={m.id} className="text-xs">
                        <div className="font-medium">{m.incident_type}</div>
                        <div className="text-muted-foreground">{m.location} • {m.required_agents} агентов</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="absolute bottom-4 right-4 bg-background/95 backdrop-blur-sm rounded-lg p-3 shadow-lg">
                  <h4 className="font-semibold text-sm mb-2">Легенда</h4>
                  <div className="space-y-1 text-xs">
                    <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-green-500" /><span>Здоров</span></div>
                    <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-yellow-500" /><span>Предупреждение</span></div>
                    <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500" /><span>Офлайн</span></div>
                    <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-600 animate-pulse" /><span>Активная миссия</span></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Dashboard view */}
        {view === 'dashboard' && (
          <>
            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Активные миссии</CardDescription>
                  <CardTitle className="text-3xl">
                    {loadingMissions ? '…' : activeMissions.length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Доступные агенты</CardDescription>
                  <CardTitle className="text-3xl">
                    {loadingAgents ? '…' : availableAgents.length}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Назначенных секторов</CardDescription>
                  <CardTitle className="text-3xl">
                    {loadingMissions ? '…' : activeSectors}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-3">
                  <CardDescription>Завершённые миссии</CardDescription>
                  <CardTitle className="text-3xl">
                    {loadingMissions ? '…' : completedMissions.length}
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>

            {/* Missions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Radio className="w-5 h-5" />
                  Текущие миссии
                </CardTitle>
                <CardDescription>Список активных и запланированных поисковых операций</CardDescription>
              </CardHeader>
              <CardContent>
                {loadingMissions ? (
                  <p className="text-muted-foreground text-sm py-8 text-center">Загрузка миссий…</p>
                ) : missions.length === 0 ? (
                  <p className="text-muted-foreground text-sm py-8 text-center">Миссии не найдены. Создайте первую миссию.</p>
                ) : (
                  <div className="space-y-4">
                    {missions.map(mission => {
                      const assignments = missionAssignments[mission.id] ?? [];
                      return (
                        <div
                          key={mission.id}
                          className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-accent/50 transition-colors"
                        >
                          <div className="flex items-center gap-4">
                            <div className={`w-2 h-2 rounded-full ${getMissionStatusColor(mission.status)}`} />
                            <div>
                              <div className="font-semibold text-foreground">{mission.incident_type}</div>
                              <div className="text-sm text-muted-foreground flex items-center gap-4 mt-1">
                                <span className="flex items-center gap-1">
                                  <Clock className="w-3 h-3" />
                                  {new Date(mission.created_at).toLocaleString('ru-RU')}
                                </span>
                                <span>{mission.required_agents} агентов</span>
                                <span>{assignments.length} секторов</span>
                                <span className="flex items-center gap-1">
                                  <MapPin className="w-3 h-3" />
                                  {mission.location}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <Badge variant="outline">{getMissionStatusText(mission.status)}</Badge>
                            <Dialog>
                              <DialogTrigger asChild>
                                <Button size="sm" variant="outline">Детали</Button>
                              </DialogTrigger>
                              <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
                                <DialogHeader>
                                  <DialogTitle className="flex items-center gap-2">
                                    {mission.incident_type}
                                    <Badge className={getPriorityColor(mission.priority)}>
                                      {getPriorityText(mission.priority)}
                                    </Badge>
                                  </DialogTitle>
                                  <DialogDescription>
                                    ID: {mission.id} • Создано: {new Date(mission.created_at).toLocaleString('ru-RU')}
                                    {' '}• Местоположение: {mission.location}
                                  </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-6 py-4">
                                  <div>
                                    <h3 className="font-semibold mb-2">Статистика</h3>
                                    <div className="grid grid-cols-3 gap-4">
                                      <div className="border rounded-lg p-3">
                                        <div className="text-2xl font-bold">{mission.required_agents}</div>
                                        <div className="text-xs text-muted-foreground">Агентов</div>
                                      </div>
                                      <div className="border rounded-lg p-3">
                                        <div className="text-2xl font-bold">{assignments.length}</div>
                                        <div className="text-xs text-muted-foreground">Секторов</div>
                                      </div>
                                      <div className="border rounded-lg p-3">
                                        <div className="text-2xl font-bold">
                                          {assignments.filter(a => a.route_status === 'COMPLETED').length}
                                        </div>
                                        <div className="text-xs text-muted-foreground">Завершено</div>
                                      </div>
                                    </div>
                                  </div>
                                  {assignments.length > 0 && (
                                    <div>
                                      <h3 className="font-semibold mb-2">Назначения</h3>
                                      <div className="space-y-2">
                                        {assignments.map(a => (
                                          <div key={a.zone_id} className="flex items-center justify-between p-3 border rounded-lg">
                                            <div>
                                              <div className="font-medium text-sm">Зона {a.zone_code}</div>
                                              {a.agent_name && (
                                                <div className="text-xs text-muted-foreground">Агент: {a.agent_name}</div>
                                              )}
                                            </div>
                                            <Badge variant={a.route_status === 'COMPLETED' ? 'default' : 'outline'}>
                                              {a.route_status ?? 'Не назначен'}
                                            </Badge>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </DialogContent>
                            </Dialog>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Agents */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Статус агентов
                </CardTitle>
                <CardDescription>Мониторинг доступности, заряда и качества связи роботизированных устройств</CardDescription>
              </CardHeader>
              <CardContent>
                {loadingAgents ? (
                  <p className="text-muted-foreground text-sm py-8 text-center">Загрузка данных агентов…</p>
                ) : agents.length === 0 ? (
                  <p className="text-muted-foreground text-sm py-8 text-center">Нет данных об агентах. Убедитесь, что сервис мониторинга работает.</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {agents.map(agent => (
                      <div
                        key={agent.agent_id}
                        className="p-4 border border-border rounded-lg space-y-3 hover:border-primary/50 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="font-semibold text-foreground">Агент-{agent.agent_id}</div>
                          <div className={`w-2 h-2 rounded-full ${getAgentHealthColor(agent.health_state)}`} />
                        </div>
                        <div className="text-sm text-muted-foreground">
                          <div className="flex items-center gap-2 mb-2">
                            <Clock className="w-4 h-4" />
                            {new Date(agent.last_seen_at).toLocaleTimeString('ru-RU')}
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1">
                              <Battery className={`w-4 h-4 ${getBatteryColor(agent.battery_level)}`} />
                              <span className={getBatteryColor(agent.battery_level)}>{agent.battery_level}%</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Wifi className={`w-4 h-4 ${getLinkColor(agent.link_status)}`} />
                              <span className={getLinkColor(agent.link_status)}>{agent.link_status}</span>
                            </div>
                          </div>
                          <div className="text-xs mt-2">Статус: {agent.mission_status}</div>
                        </div>
                        <Badge variant="secondary" className="w-full justify-center">
                          {getAgentHealthText(agent.health_state)}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* FAQ */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  Часто задаваемые вопросы
                </CardTitle>
                <CardDescription>Ответы на основные вопросы о работе системы координации</CardDescription>
              </CardHeader>
              <CardContent>
                <Accordion type="single" collapsible className="w-full">
                  {faqItems.map((item, index) => (
                    <AccordionItem key={index} value={`item-${index}`}>
                      <AccordionTrigger className="text-left hover:text-primary">
                        {item.question}
                      </AccordionTrigger>
                      <AccordionContent className="text-muted-foreground">
                        {item.answer}
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </CardContent>
            </Card>

            {/* Architecture info */}
            <Card className="bg-accent/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5" />
                  Архитектура системы
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h3 className="font-semibold text-foreground">Микросервис координации</h3>
                    <p className="text-sm text-muted-foreground">
                      Принимает запросы от внешних клиентов, формирует задачи, выделяет сектора обследования
                      и назначает агентов на зоны поиска
                    </p>
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-semibold text-foreground">Микросервис мониторинга</h3>
                    <p className="text-sm text-muted-foreground">
                      Предоставляет актуальную информацию о доступности устройств, уровне заряда и качестве
                      связи для оптимального распределения задач
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default SearchCoordinationDashboard;
