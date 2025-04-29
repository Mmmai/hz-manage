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

        active_rules = ProxyAssignRule.objects.filter(active=True)

        proxy_rules = {}
        for rule in active_rules:
            if rule.proxy.id not in proxy_rules:
                proxy_rules[rule.proxy.id] = {
                    'proxy': rule.proxy,
                    'rules': {
                        'ip_exclude': [],
                        'ip_list': [],
                        'ip_cidr': [],
                        'ip_range': [],
                        'ip_regex': []
                    }
                }
            proxy_rules[rule.proxy.id]['rules'][rule.type].append(rule)

        excluded_proxies = set()

        for proxy_id, proxy_data in proxy_rules.items():
            for rule in proxy_data['rules']['ip_exclude']:
                if ProxyAssignment._match_rule(rule, ip_address):
                    excluded_proxies.add(proxy_id)
                    break

        rule_types_by_priority = ['ip_list', 'ip_cidr', 'ip_range', 'ip_regex']

        for rule_type in rule_types_by_priority:
            for proxy_id, proxy_data in proxy_rules.items():
                if proxy_id in excluded_proxies:
                    continue

                for rule in proxy_data['rules'][rule_type]:
                    if ProxyAssignment._match_rule(rule, ip_address):
                        return proxy_data['proxy']

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

            start, end = rule_value.split('-')
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
