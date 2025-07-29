"""
MCPStore API 响应模型
包含所有API端点使用的请求和响应模型
"""

from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


# === 监控相关的响应模型 ===

class ToolUsageStatsResponse(BaseModel):
    """工具使用统计响应"""
    tool_name: str = Field(description="工具名称")
    service_name: str = Field(description="服务名称")
    execution_count: int = Field(description="执行次数")
    last_executed: Optional[str] = Field(description="最后执行时间")
    average_response_time: float = Field(description="平均响应时间")
    success_rate: float = Field(description="成功率")

class ToolExecutionRecordResponse(BaseModel):
    """工具执行记录响应"""
    id: str = Field(description="记录ID")
    tool_name: str = Field(description="工具名称")
    service_name: str = Field(description="服务名称")
    params: Dict[str, Any] = Field(description="执行参数")
    result: Optional[Any] = Field(description="执行结果")
    error: Optional[str] = Field(description="错误信息")
    response_time: float = Field(description="响应时间(毫秒)")
    execution_time: str = Field(description="执行时间")
    timestamp: int = Field(description="时间戳")

class ToolRecordsSummaryResponse(BaseModel):
    """工具记录汇总响应"""
    total_executions: int = Field(description="总执行次数")
    by_tool: Dict[str, Dict[str, Any]] = Field(description="按工具统计")
    by_service: Dict[str, Dict[str, Any]] = Field(description="按服务统计")

class ToolRecordsResponse(BaseModel):
    """工具记录完整响应"""
    executions: List[ToolExecutionRecordResponse] = Field(description="执行记录列表")
    summary: ToolRecordsSummaryResponse = Field(description="汇总统计")

class NetworkEndpointResponse(BaseModel):
    """网络端点响应"""
    endpoint_name: str = Field(description="端点名称")
    url: str = Field(description="端点URL")
    status: str = Field(description="状态")
    response_time: float = Field(description="响应时间")
    last_checked: str = Field(description="最后检查时间")
    uptime_percentage: float = Field(description="可用性百分比")

class SystemResourceInfoResponse(BaseModel):
    """系统资源信息响应"""
    server_uptime: str = Field(description="服务器运行时间")
    memory_total: int = Field(description="总内存")
    memory_used: int = Field(description="已用内存")
    memory_percentage: float = Field(description="内存使用率")
    disk_usage_percentage: float = Field(description="磁盘使用率")
    network_traffic_in: int = Field(description="网络入流量")
    network_traffic_out: int = Field(description="网络出流量")

class AddAlertRequest(BaseModel):
    """添加告警请求"""
    type: str = Field(description="告警类型: warning, error, info")
    title: str = Field(description="告警标题")
    message: str = Field(description="告警消息")
    service_name: Optional[str] = Field(None, description="相关服务名称")

class NetworkEndpointCheckRequest(BaseModel):
    """网络端点检查请求"""
    endpoints: List[Dict[str, str]] = Field(description="端点列表")

# === 健康状态相关响应模型 ===
class ServiceHealthResponse(BaseModel):
    """服务健康状态响应"""
    service_name: str = Field(description="服务名称")
    status: str = Field(description="健康状态: healthy, warning, slow, unhealthy, unknown")
    response_time: float = Field(description="最近响应时间（秒）")
    last_check_time: float = Field(description="最后检查时间戳")
    consecutive_failures: int = Field(description="连续失败次数")
    average_response_time: float = Field(description="平均响应时间（秒）")
    adaptive_timeout: float = Field(description="智能调整的超时时间（秒）")
    error_message: Optional[str] = Field(None, description="错误信息")
    details: Dict[str, Any] = Field(default_factory=dict, description="详细信息")

class HealthSummaryResponse(BaseModel):
    """健康状态汇总响应"""
    total_services: int = Field(description="总服务数量")
    healthy_count: int = Field(description="健康服务数量")
    warning_count: int = Field(description="警告状态服务数量")
    slow_count: int = Field(description="慢响应服务数量")
    unhealthy_count: int = Field(description="不健康服务数量")
    services: Dict[str, ServiceHealthResponse] = Field(description="各服务健康状态详情")

# === Agent统计相关响应模型 ===
class AgentServiceSummaryResponse(BaseModel):
    """Agent服务摘要响应"""
    service_name: str = Field(description="服务名称")
    service_type: str = Field(description="服务类型")
    status: str = Field(description="服务状态: healthy, warning, slow, unhealthy, unknown")
    tool_count: int = Field(description="工具数量")
    last_used: Optional[str] = Field(None, description="最后使用时间")
    client_id: Optional[str] = Field(None, description="客户端ID")
    response_time: Optional[float] = Field(None, description="最近响应时间（秒）")
    health_details: Optional[Dict[str, Any]] = Field(None, description="健康状态详情")

class AgentStatisticsResponse(BaseModel):
    """Agent统计信息响应"""
    agent_id: str = Field(description="Agent ID")
    service_count: int = Field(description="服务数量")
    tool_count: int = Field(description="工具数量")
    healthy_services: int = Field(description="健康服务数量")
    unhealthy_services: int = Field(description="不健康服务数量")
    total_tool_executions: int = Field(description="总工具执行次数")
    last_activity: Optional[str] = Field(None, description="最后活动时间")
    services: List[AgentServiceSummaryResponse] = Field(description="服务列表")

class AgentsSummaryResponse(BaseModel):
    """所有Agent汇总信息响应"""
    total_agents: int = Field(description="总Agent数量")
    active_agents: int = Field(description="活跃Agent数量")
    total_services: int = Field(description="总服务数量")
    total_tools: int = Field(description="总工具数量")
    store_services: int = Field(description="Store级别服务数量")
    store_tools: int = Field(description="Store级别工具数量")
    agents: List[AgentStatisticsResponse] = Field(description="Agent列表")

# === 工具执行请求模型 ===
class SimpleToolExecutionRequest(BaseModel):
    """简化的工具执行请求模型（用于API）"""
    tool_name: str = Field(..., description="工具名称")
    args: Dict[str, Any] = Field(default_factory=dict, description="工具参数")
    service_name: Optional[str] = Field(None, description="服务名称（可选，会自动推断）")

# === 监控配置模型 ===
class MonitoringConfig(BaseModel):
    """监控配置模型"""
    heartbeat_interval_seconds: Optional[int] = Field(default=None, ge=10, le=300, description="心跳检查间隔（秒），范围10-300")
    reconnection_interval_seconds: Optional[int] = Field(default=None, ge=10, le=600, description="重连尝试间隔（秒），范围10-600")
    cleanup_interval_hours: Optional[int] = Field(default=None, ge=1, le=24, description="资源清理间隔（小时），范围1-24")
    max_reconnection_queue_size: Optional[int] = Field(default=None, ge=10, le=200, description="最大重连队列大小，范围10-200")
    max_heartbeat_history_hours: Optional[int] = Field(default=None, ge=1, le=168, description="心跳历史保留时间（小时），范围1-168")
    http_timeout_seconds: Optional[int] = Field(default=None, ge=1, le=30, description="HTTP超时时间（秒），范围1-30")

    # === 新增：分层超时配置 ===
    local_service_ping_timeout: Optional[int] = Field(default=None, ge=1, le=10, description="本地服务ping超时时间（秒），范围1-10")
    remote_service_ping_timeout: Optional[int] = Field(default=None, ge=1, le=30, description="远程服务ping超时时间（秒），范围1-30")
    startup_wait_time: Optional[int] = Field(default=None, ge=1, le=10, description="服务启动等待时间（秒），范围1-10")

    # === 新增：健康状态阈值配置 ===
    healthy_response_threshold: Optional[float] = Field(default=None, ge=0.1, le=5.0, description="健康状态响应时间阈值（秒），范围0.1-5.0")
    warning_response_threshold: Optional[float] = Field(default=None, ge=0.5, le=10.0, description="警告状态响应时间阈值（秒），范围0.5-10.0")
    slow_response_threshold: Optional[float] = Field(default=None, ge=1.0, le=30.0, description="慢响应状态响应时间阈值（秒），范围1.0-30.0")

    # === 新增：智能超时调整配置 ===
    enable_adaptive_timeout: Optional[bool] = Field(default=None, description="是否启用智能超时调整")
    adaptive_timeout_multiplier: Optional[float] = Field(default=None, ge=1.5, le=5.0, description="智能超时倍数，范围1.5-5.0")
    response_time_history_size: Optional[int] = Field(default=None, ge=5, le=100, description="响应时间历史记录大小，范围5-100")
