# DatabaseFaultInjectionSchedule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**benchmark** | **str** | 基准数据库 | [optional] 
**created_at** | **str** | 创建时间 | [optional] 
**description** | **str** | 描述（可选字段） | [optional] 
**display_config** | **str** | 面向用户的展示配置 | [optional] 
**end_time** | **str** | 预计故障结束时间 | [optional] 
**engine_config** | **str** | 面向系统的运行配置 | [optional] 
**fault_type** | **int** | 故障类型 | [optional] 
**id** | **int** | 唯一标识 | [optional] 
**injection_name** | **str** | 在k8s资源里注入的名字 | [optional] 
**labels** | **Dict[str, str]** | 用户自定义标签，JSONB格式存储 key-value pairs | [optional] 
**pre_duration** | **int** | 正常数据时间 | [optional] 
**start_time** | **str** | 预计故障开始时间 | [optional] 
**status** | **int** | -1: 已删除 0: 初始状态 1: 注入结束且失败 2: 注入结束且成功 3: 收集数据失败 4:收集数据成功 | [optional] 
**task_id** | **str** | 从属什么 taskid | [optional] 
**updated_at** | **str** | 更新时间 | [optional] 

## Example

```python
from rcabench.openapi.models.database_fault_injection_schedule import DatabaseFaultInjectionSchedule

# TODO update the JSON string below
json = "{}"
# create an instance of DatabaseFaultInjectionSchedule from a JSON string
database_fault_injection_schedule_instance = DatabaseFaultInjectionSchedule.from_json(json)
# print the JSON string representation of the object
print(DatabaseFaultInjectionSchedule.to_json())

# convert the object into a dict
database_fault_injection_schedule_dict = database_fault_injection_schedule_instance.to_dict()
# create an instance of DatabaseFaultInjectionSchedule from a dict
database_fault_injection_schedule_from_dict = DatabaseFaultInjectionSchedule.from_dict(database_fault_injection_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


