import re
import ipaddress
import logging
from django.db.models import Q
from ..models import ZabbixProxy, ProxyAssignRule

logger = logging.getLogger(__name__)


class ProxyAssignment:
    """代理分配服务"""

    @staticmethod
    def find_proxy_for_ip(ip_address):
        if not ip_address:
            return None

        # 获取所有活跃的规则，按规则类型的优先级排序
        active_rules = ProxyAssignRule.objects.filter(active=True)

        # 首先检查IP排除规则
        exclude_rules = active_rules.filter(type='ip_exclude')
        for rule in exclude_rules:
            if ProxyAssignment._match_rule(rule, ip_address):
                return None

        # 再检查IP列表规则（精确匹配）
        list_rules = active_rules.filter(type='ip_list')
        for rule in list_rules:
            if ProxyAssignment._match_rule(rule, ip_address):
                return rule.proxy

        # 检查IP子网规则（CIDR）
        cidr_rules = active_rules.filter(type='ip_cidr')
        for rule in cidr_rules:
            if ProxyAssignment._match_rule(rule, ip_address):
                return rule.proxy

        # 检查IP范围规则
        range_rules = active_rules.filter(type='ip_range')
        for rule in range_rules:
            if ProxyAssignment._match_rule(rule, ip_address):
                return rule.proxy

        # 最后检查IP正则规则
        regex_rules = active_rules.filter(type='ip_regex')
        for rule in regex_rules:
            if ProxyAssignment._match_rule(rule, ip_address):
                return rule.proxy

        return None

    @staticmethod
    def _match_rule(rule, ip_address):
        """检查IP是否匹配特定规则"""
        try:
            if rule.type == 'ip_exclude':
                return ProxyAssignment._match_ip_exclude(rule.rule, ip_address)

            elif rule.type == 'ip_list':
                return ProxyAssignment._match_ip_list(rule.rule, ip_address)

            elif rule.type == 'ip_cidr':
                return ProxyAssignment._match_ip_cidr(rule.rule, ip_address)

            elif rule.type == 'ip_range':
                return ProxyAssignment._match_ip_range(rule.rule, ip_address)

            elif rule.type == 'ip_regex':
                return ProxyAssignment._match_ip_regex(rule.rule, ip_address)

        except Exception as e:
            logger.error(f"匹配规则 {rule.id} 时发生错误: {e}")

        return False

    @staticmethod
    def _match_ip_exclude(rule_value, ip_address):
        """匹配IP排除规则（与其他规则相反，匹配则表示应该排除）"""
        ip_list = [ip.strip() for ip in rule_value.split(',') if ip.strip()]
        return ip_address not in ip_list

    @staticmethod
    def _match_ip_list(rule_value, ip_address):
        """匹配IP列表规则（精确匹配）"""
        ip_list = [ip.strip() for ip in rule_value.split(',') if ip.strip()]
        return ip_address in ip_list

    @staticmethod
    def _match_ip_cidr(rule_value, ip_address):
        """匹配IP子网划分规则（CIDR）"""
        try:
            host_ip = ipaddress.ip_address(ip_address)
            for subnet_rule in rule_value.split(','):
                network = ipaddress.ip_network(subnet_rule, strict=False)
                if host_ip in network:
                    return True
        except Exception as e:
            logger.error(f"Error occurred while matching CIDR rule: {str(e)}")

        return False

    @staticmethod
    def _match_ip_range(rule_value, ip_address):
        """检查IP是否在范围内"""
        try:
            host_ip = ipaddress.ip_address(ip_address)

            # 支持多个范围，用逗号分隔
            for range_expr in rule_value.split(','):
                range_expr = range_expr.strip()
                start, end = range_expr.split('-')
                start_ip = ipaddress.ip_address(start.strip())
                end_ip = ipaddress.ip_address(end.strip())
                if start_ip <= host_ip <= end_ip:
                    return True
        except Exception as e:
            logger.error(f"Error occurred while matching IP range: {str(e)}")

        return False

    @staticmethod
    def _match_ip_regex(rule_value, ip_address):
        """使用正则表达式匹配IP"""
        try:
            # 支持多个正则表达式，用换行符分隔
            for pattern_str in rule_value.strip().split('\n'):
                if not pattern_str.strip():
                    continue

                pattern = re.compile(pattern_str.strip())
                if pattern.match(ip_address):
                    return True
        except Exception as e:
            logger.error(f"Error occurred while matching regex rule: {str(e)}")

        return False
