"""
MCPStore API - 监控相关路由
包含所有监控、统计、健康检查等相关的API端点
"""

from fastapi import APIRouter
from mcpstore.core.models.common import APIResponse

from .api_decorators import handle_exceptions, get_store
from .api_models import (
    AgentsSummaryResponse, AgentStatisticsResponse, AgentServiceSummaryResponse,
    MonitoringConfig, AddAlertRequest, ServiceHealthResponse, HealthSummaryResponse
)

# 创建监控相关的路由器
monitoring_router = APIRouter()

# === Agent统计功能 ===
@monitoring_router.get("/agents_summary", response_model=APIResponse)
@handle_exceptions
async def get_agents_summary():
    """
    获取所有Agent的统计摘要信息
    
    Returns:
        APIResponse: 包含所有Agent统计信息的响应
        
    Response Data Structure:
        {
            "total_agents": int,           # 总Agent数量
            "active_agents": int,          # 活跃Agent数量（有服务的Agent）
            "total_services": int,         # 总服务数量（包括Store和所有Agent）
            "total_tools": int,            # 总工具数量（包括Store和所有Agent）
            "store_services": int,         # Store级别服务数量
            "store_tools": int,            # Store级别工具数量
            "agents": [                    # Agent详细列表
                {
                    "agent_id": str,
                    "service_count": int,
                    "tool_count": int,
                    "healthy_services": int,
                    "unhealthy_services": int,
                    "total_tool_executions": int,
                    "last_activity": str,
                    "services": [
                        {
                            "service_name": str,
                            "service_type": str,
                            "status": str,
                            "tool_count": int,
                            "last_used": str,
                            "client_id": str
                        }
                    ]
                }
            ]
        }
    """
    try:
        store = get_store()
        
        # 调用SDK的Agent统计功能
        summary = await store.for_store().get_agents_summary_async()
        
        # 转换为API响应格式
        agents_data = []
        for agent_stats in summary.agents:
            services_data = []
            for service in agent_stats.services:
                services_data.append(AgentServiceSummaryResponse(
                    service_name=service.service_name,
                    service_type=service.service_type,
                    status=service.status,
                    tool_count=service.tool_count,
                    last_used=service.last_used.isoformat() if service.last_used else None,
                    client_id=service.client_id
                ).dict())
            
            agents_data.append(AgentStatisticsResponse(
                agent_id=agent_stats.agent_id,
                service_count=agent_stats.service_count,
                tool_count=agent_stats.tool_count,
                healthy_services=agent_stats.healthy_services,
                unhealthy_services=agent_stats.unhealthy_services,
                total_tool_executions=agent_stats.total_tool_executions,
                last_activity=agent_stats.last_activity.isoformat() if agent_stats.last_activity else None,
                services=services_data
            ).dict())
        
        response_data = AgentsSummaryResponse(
            total_agents=summary.total_agents,
            active_agents=summary.active_agents,
            total_services=summary.total_services,
            total_tools=summary.total_tools,
            store_services=summary.store_services,
            store_tools=summary.store_tools,
            agents=agents_data
        ).dict()
        
        return APIResponse(
            success=True,
            data=response_data,
            message=f"Agents summary retrieved successfully. Found {summary.total_agents} agents, {summary.active_agents} active."
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            data={
                "total_agents": 0,
                "active_agents": 0,
                "total_services": 0,
                "total_tools": 0,
                "store_services": 0,
                "store_tools": 0,
                "agents": []
            },
            message=f"Failed to get agents summary: {str(e)}"
        )

# === 监控配置管理 ===
@monitoring_router.get("/monitoring/config", response_model=APIResponse)
@handle_exceptions
async def get_monitoring_config():
    """获取监控配置"""
    try:
        store = get_store()
        config = await store.for_store().get_monitoring_config_async()
        
        return APIResponse(
            success=True,
            data=config,
            message="Monitoring configuration retrieved successfully"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to get monitoring configuration: {str(e)}"
        )

@monitoring_router.post("/monitoring/config", response_model=APIResponse)
@handle_exceptions
async def update_monitoring_config(config: MonitoringConfig):
    """更新监控配置"""
    try:
        store = get_store()
        
        # 转换为字典格式，过滤None值
        config_dict = {k: v for k, v in config.dict().items() if v is not None}
        
        result = await store.for_store().update_monitoring_config_async(config_dict)
        
        return APIResponse(
            success=bool(result),
            data=result,
            message="Monitoring configuration updated successfully" if result else "Failed to update monitoring configuration"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to update monitoring configuration: {str(e)}"
        )

# === 告警管理 ===
@monitoring_router.post("/monitoring/alerts", response_model=APIResponse)
@handle_exceptions
async def add_alert(alert: AddAlertRequest):
    """添加告警"""
    try:
        store = get_store()
        
        alert_data = {
            "type": alert.type,
            "title": alert.title,
            "message": alert.message,
            "service_name": alert.service_name
        }
        
        result = await store.for_store().add_alert_async(alert_data)
        
        return APIResponse(
            success=bool(result),
            data=result,
            message="Alert added successfully" if result else "Failed to add alert"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to add alert: {str(e)}"
        )

@monitoring_router.get("/monitoring/alerts", response_model=APIResponse)
@handle_exceptions
async def get_alerts(limit: int = 50):
    """获取告警列表"""
    try:
        store = get_store()
        alerts = await store.for_store().get_alerts_async(limit)
        
        return APIResponse(
            success=True,
            data=alerts,
            message=f"Retrieved {len(alerts) if isinstance(alerts, list) else 0} alerts"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=[],
            message=f"Failed to get alerts: {str(e)}"
        )

@monitoring_router.delete("/monitoring/alerts", response_model=APIResponse)
@handle_exceptions
async def clear_alerts():
    """清除所有告警"""
    try:
        store = get_store()
        result = await store.for_store().clear_alerts_async()
        
        return APIResponse(
            success=bool(result),
            data=result,
            message="All alerts cleared successfully" if result else "Failed to clear alerts"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data=False,
            message=f"Failed to clear alerts: {str(e)}"
        )

# === 性能监控 ===
@monitoring_router.get("/monitoring/performance", response_model=APIResponse)
@handle_exceptions
async def get_performance_metrics():
    """获取性能指标"""
    try:
        store = get_store()
        metrics = await store.for_store().get_performance_metrics_async()
        
        return APIResponse(
            success=True,
            data=metrics,
            message="Performance metrics retrieved successfully"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to get performance metrics: {str(e)}"
        )

@monitoring_router.get("/monitoring/usage_stats", response_model=APIResponse)
@handle_exceptions
async def get_usage_statistics():
    """获取使用统计"""
    try:
        store = get_store()
        stats = await store.for_store().get_usage_stats_async()
        
        return APIResponse(
            success=True,
            data=stats,
            message="Usage statistics retrieved successfully"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to get usage statistics: {str(e)}"
        )

# === 健康状态管理 ===
@monitoring_router.get("/health/summary", response_model=APIResponse)
@handle_exceptions
async def get_health_summary():
    """获取所有服务的健康状态汇总"""
    try:
        store = get_store()

        # 从Orchestrator获取健康管理器
        orchestrator = store.orchestrator
        health_summary = orchestrator.health_manager.get_all_health_summary()

        # 转换为API响应格式
        services_health = {}
        for service_name, service_data in health_summary["services"].items():
            services_health[service_name] = ServiceHealthResponse(
                service_name=service_data["service_name"],
                status=service_data["current_status"],
                response_time=service_data.get("average_response_time", 0.0),
                last_check_time=service_data["last_check_time"],
                consecutive_failures=service_data["consecutive_failures"],
                average_response_time=service_data["average_response_time"],
                adaptive_timeout=service_data["adaptive_timeout"],
                error_message=None,
                details={"response_history_size": service_data["response_history_size"]}
            ).dict()

        response_data = HealthSummaryResponse(
            total_services=health_summary["total_services"],
            healthy_count=health_summary["healthy_count"],
            warning_count=health_summary["warning_count"],
            slow_count=health_summary["slow_count"],
            unhealthy_count=health_summary["unhealthy_count"],
            services=services_health
        ).dict()

        return APIResponse(
            success=True,
            data=response_data,
            message=f"Health summary retrieved successfully. {health_summary['total_services']} services tracked."
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data={
                "total_services": 0,
                "healthy_count": 0,
                "warning_count": 0,
                "slow_count": 0,
                "unhealthy_count": 0,
                "services": {}
            },
            message=f"Failed to get health summary: {str(e)}"
        )

@monitoring_router.get("/health/service/{service_name}", response_model=APIResponse)
@handle_exceptions
async def get_service_health(service_name: str):
    """获取特定服务的详细健康状态"""
    try:
        store = get_store()

        # 从Orchestrator获取健康管理器
        orchestrator = store.orchestrator

        if service_name not in orchestrator.health_manager.service_trackers:
            return APIResponse(
                success=False,
                data={},
                message=f"Service '{service_name}' not found in health tracking"
            )

        tracker = orchestrator.health_manager.service_trackers[service_name]
        service_summary = tracker.get_health_summary()

        response_data = ServiceHealthResponse(
            service_name=service_summary["service_name"],
            status=service_summary["current_status"],
            response_time=service_summary["average_response_time"],
            last_check_time=service_summary["last_check_time"],
            consecutive_failures=service_summary["consecutive_failures"],
            average_response_time=service_summary["average_response_time"],
            adaptive_timeout=service_summary["adaptive_timeout"],
            error_message=None,
            details={"response_history_size": service_summary["response_history_size"]}
        ).dict()

        return APIResponse(
            success=True,
            data=response_data,
            message=f"Health status retrieved for service '{service_name}'"
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to get health status for service '{service_name}': {str(e)}"
        )

@monitoring_router.post("/health/check/{service_name}", response_model=APIResponse)
@handle_exceptions
async def trigger_health_check(service_name: str):
    """手动触发特定服务的健康检查"""
    try:
        store = get_store()

        # 从Orchestrator触发健康检查
        orchestrator = store.orchestrator
        health_result = await orchestrator.check_service_health_detailed(service_name)

        response_data = ServiceHealthResponse(
            service_name=service_name,
            status=health_result.status.value,
            response_time=health_result.response_time,
            last_check_time=health_result.timestamp,
            consecutive_failures=health_result.details.get("consecutive_failures", 0),
            average_response_time=health_result.details.get("avg_response_time", 0.0),
            adaptive_timeout=0.0,  # 会在下次获取时更新
            error_message=health_result.error_message,
            details=health_result.details
        ).dict()

        return APIResponse(
            success=True,
            data=response_data,
            message=f"Health check completed for service '{service_name}'. Status: {health_result.status.value}"
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to check health for service '{service_name}': {str(e)}"
        )

@monitoring_router.post("/tools/refresh", response_model=APIResponse)
@handle_exceptions
async def refresh_all_tools():
    """手动刷新所有服务的工具列表"""
    try:
        store = get_store()
        orchestrator = store.orchestrator

        if not orchestrator.tools_update_monitor:
            return APIResponse(
                success=False,
                data={},
                message="Tools update monitor is not enabled"
            )

        # 手动更新所有服务的工具列表
        results = await orchestrator.tools_update_monitor.manual_update_all()

        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        return APIResponse(
            success=True,
            data={
                "updated_services": success_count,
                "total_services": total_count,
                "results": results
            },
            message=f"Tools refresh completed: {success_count}/{total_count} services updated successfully"
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to refresh tools: {str(e)}"
        )

@monitoring_router.post("/tools/refresh/{service_name}", response_model=APIResponse)
@handle_exceptions
async def refresh_service_tools(service_name: str):
    """手动刷新特定服务的工具列表"""
    try:
        store = get_store()
        orchestrator = store.orchestrator

        if not orchestrator.tools_update_monitor:
            return APIResponse(
                success=False,
                data={},
                message="Tools update monitor is not enabled"
            )

        # 手动更新特定服务的工具列表
        success = await orchestrator.tools_update_monitor.manual_update_service(service_name)

        if success:
            return APIResponse(
                success=True,
                data={"service_name": service_name},
                message=f"Tools refreshed successfully for service '{service_name}'"
            )
        else:
            return APIResponse(
                success=False,
                data={"service_name": service_name},
                message=f"Failed to refresh tools for service '{service_name}'"
            )

    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to refresh tools for service '{service_name}': {str(e)}"
        )

@monitoring_router.get("/tools/update_status", response_model=APIResponse)
@handle_exceptions
async def get_tools_update_status():
    """获取工具更新状态"""
    try:
        store = get_store()
        orchestrator = store.orchestrator

        if not orchestrator.tools_update_monitor:
            return APIResponse(
                success=True,
                data={
                    "enabled": False,
                    "message": "Tools update monitor is not enabled"
                },
                message="Tools update monitoring is disabled"
            )

        status = orchestrator.tools_update_monitor.get_update_status()

        return APIResponse(
            success=True,
            data=status,
            message="Tools update status retrieved successfully"
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data={},
            message=f"Failed to get tools update status: {str(e)}"
        )
