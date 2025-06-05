from typing import Dict, List, Optional
from dataclasses import dataclass
import re

@dataclass
class Component:
    id: str
    type: str
    properties: Dict[str, any]

class CompatibilityAgent:
    def __init__(self):
        # CPU socket mapping based on series and generation
        self.cpu_socket_map = {
            # AMD Ryzen Series
            'Ryzen 3': {
                '1000': 'AM4',
                '2000': 'AM4',
                '3000': 'AM4',
                '4000': 'AM4',
                '5000': 'AM4',
                '7000': 'AM5'
            },
            'Ryzen 5': {
                '1000': 'AM4',
                '2000': 'AM4',
                '3000': 'AM4',
                '4000': 'AM4',
                '5000': 'AM4',
                '7000': 'AM5'
            },
            'Ryzen 7': {
                '1000': 'AM4',
                '2000': 'AM4',
                '3000': 'AM4',
                '4000': 'AM4',
                '5000': 'AM4',
                '7000': 'AM5'
            },
            'Ryzen 9': {
                '3000': 'AM4',
                '4000': 'AM4',
                '5000': 'AM4',
                '7000': 'AM5'
            },
            # Intel Core Series
            'Core i3': {
                '10': 'LGA1200',
                '11': 'LGA1200',
                '12': 'LGA1700',
                '13': 'LGA1700',
                '14': 'LGA1700'
            },
            'Core i5': {
                '10': 'LGA1200',
                '11': 'LGA1200',
                '12': 'LGA1700',
                '13': 'LGA1700',
                '14': 'LGA1700'
            },
            'Core i7': {
                '10': 'LGA1200',
                '11': 'LGA1200',
                '12': 'LGA1700',
                '13': 'LGA1700',
                '14': 'LGA1700'
            },
            'Core i9': {
                '10': 'LGA1200',
                '11': 'LGA1200',
                '12': 'LGA1700',
                '13': 'LGA1700',
                '14': 'LGA1700'
            }
        }
        
        self.compatibility_rules = {
            'cpu_motherboard': self._check_cpu_motherboard_compatibility,
            'ram_motherboard': self._check_ram_motherboard_compatibility,
            'psu_components': self._check_psu_compatibility,
            'cooling_case': self._check_cooling_case_compatibility,
            'motherboard_case': self._check_motherboard_case_compatibility,
            'storage_motherboard': self._check_storage_motherboard_compatibility,
            'network_motherboard': self._check_network_motherboard_compatibility,
            'sound_motherboard': self._check_sound_motherboard_compatibility,
            'fan_controller_case': self._check_fan_controller_case_compatibility,
            'ups_psu': self._check_ups_psu_compatibility,
            'os_memory': self._check_os_memory_compatibility
        }

    def _get_cpu_socket(self, cpu_name: str) -> Optional[str]:
        """
        Determine CPU socket type from CPU name.
        
        Args:
            cpu_name: Name of the CPU (e.g., "AMD Ryzen 5 5600X")
            
        Returns:
            Socket type if found, None otherwise
        """
        # Extract CPU series and generation
        if 'Ryzen' in cpu_name:
            # AMD Ryzen
            series_match = re.search(r'Ryzen\s+(\d)', cpu_name)
            gen_match = re.search(r'(\d{4})', cpu_name)
            
            if series_match and gen_match:
                series = f"Ryzen {series_match.group(1)}"
                gen = gen_match.group(1)[0]  # First digit of generation
                return self.cpu_socket_map.get(series, {}).get(gen)
                
        elif 'Core' in cpu_name:
            # Intel Core
            series_match = re.search(r'Core\s+(i\d)', cpu_name)
            gen_match = re.search(r'-(\d{2})', cpu_name)
            
            if series_match and gen_match:
                series = f"Core {series_match.group(1)}"
                gen = gen_match.group(1)[0]  # First digit of generation
                return self.cpu_socket_map.get(series, {}).get(gen)
                
        return None

    def check_compatibility(self, selected_parts: Dict[str, Component]) -> Dict[str, bool]:
        """
        Check compatibility between all selected parts.
        
        Args:
            selected_parts: Dictionary of selected components with their types as keys
            
        Returns:
            Dictionary containing compatibility results for each check
        """
        compatibility_results = {}
        
        # Core component compatibility checks
        if 'cpu' in selected_parts and 'motherboard' in selected_parts:
            compatibility_results['cpu_motherboard'] = self._check_cpu_motherboard_compatibility(
                selected_parts['cpu'],
                selected_parts['motherboard']
            )
            
        if 'ram' in selected_parts and 'motherboard' in selected_parts:
            compatibility_results['ram_motherboard'] = self._check_ram_motherboard_compatibility(
                selected_parts['ram'],
                selected_parts['motherboard']
            )
            
        if 'power_supply' in selected_parts:
            compatibility_results['psu_components'] = self._check_psu_compatibility(
                selected_parts['power_supply'],
                selected_parts
            )
            
        if 'cpu_cooler' in selected_parts and 'case' in selected_parts:
            compatibility_results['cooling_case'] = self._check_cooling_case_compatibility(
                selected_parts['cpu_cooler'],
                selected_parts['case']
            )
            
        # Motherboard-Case compatibility
        if 'motherboard' in selected_parts and 'case' in selected_parts:
            compatibility_results['motherboard_case'] = self._check_motherboard_case_compatibility(
                selected_parts['motherboard'],
                selected_parts['case']
            )
            
        # Storage compatibility
        if 'internal_hard_drive' in selected_parts and 'motherboard' in selected_parts:
            compatibility_results['storage_motherboard'] = self._check_storage_motherboard_compatibility(
                selected_parts['internal_hard_drive'],
                selected_parts['motherboard']
            )
            
        # Network card compatibility
        if ('wireless_network_card' in selected_parts or 'network_card' in selected_parts) and 'motherboard' in selected_parts:
            network_card = selected_parts.get('wireless_network_card') or selected_parts.get('network_card')
            compatibility_results['network_motherboard'] = self._check_network_motherboard_compatibility(
                network_card,
                selected_parts['motherboard']
            )
            
        # Sound card compatibility
        if 'sound_card' in selected_parts and 'motherboard' in selected_parts:
            compatibility_results['sound_motherboard'] = self._check_sound_motherboard_compatibility(
                selected_parts['sound_card'],
                selected_parts['motherboard']
            )
            
        # Fan controller compatibility
        if 'fan_controller' in selected_parts and 'case' in selected_parts:
            compatibility_results['fan_controller_case'] = self._check_fan_controller_case_compatibility(
                selected_parts['fan_controller'],
                selected_parts['case']
            )
            
        # UPS compatibility
        if 'ups' in selected_parts and 'power_supply' in selected_parts:
            compatibility_results['ups_psu'] = self._check_ups_psu_compatibility(
                selected_parts['ups'],
                selected_parts['power_supply']
            )
            
        # OS compatibility
        if 'operating_system' in selected_parts and 'memory' in selected_parts:
            compatibility_results['os_memory'] = self._check_os_memory_compatibility(
                selected_parts['operating_system'],
                selected_parts['memory']
            )
            
        return compatibility_results

    def _check_cpu_motherboard_compatibility(self, cpu: Component, motherboard: Component) -> bool:
        """Check if CPU is compatible with motherboard based on socket type and chipset."""
        cpu_name = cpu.properties.get('name', '')
        cpu_socket = self._get_cpu_socket(cpu_name)
        mb_socket = motherboard.properties.get('socket')
        mb_chipset = motherboard.properties.get('chipset')
        
        if not cpu_socket or not mb_socket:
            return False
            
        if cpu_socket != mb_socket:
            return False
            
        # Check chipset compatibility (if specified)
        if 'chipset_compatibility' in cpu.properties:
            if mb_chipset not in cpu.properties['chipset_compatibility']:
                return False
                
        return True

    def _check_ram_motherboard_compatibility(self, ram: Component, motherboard: Component) -> bool:
        """
        Check if RAM is compatible with motherboard based on speed and modules.
        Handles multiple RAM kits (e.g., two different 2x32GB kits for 128GB total).
        """
        # Get RAM properties from memory table schema
        ram_speed = ram.properties.get('speed', [])  # Array of speeds
        ram_modules = ram.properties.get('modules', [])  # Array of modules
        
        # Get motherboard properties
        mb_max_memory = motherboard.properties.get('max_memory', 0)  # Integer value
        mb_memory_slots = motherboard.properties.get('memory_slots', 0)  # Integer value
        
        # Calculate total memory from all modules in this RAM kit
        kit_memory = sum(module.get('capacity', 0) for module in ram_modules)
        
        # Get accumulated memory from state if it exists
        accumulated_memory = 0
        if 'accumulated_memory' in ram.properties:
            accumulated_memory = ram.properties['accumulated_memory']
        
        # Calculate total memory including accumulated memory
        total_memory = kit_memory + accumulated_memory
        
        # Check if total memory exceeds motherboard maximum
        if total_memory > mb_max_memory:
            error_msg = f"Total memory ({total_memory}GB) exceeds motherboard maximum ({mb_max_memory}GB)"
            if 'compatibility_issues' not in ram.properties:
                ram.properties['compatibility_issues'] = []
            ram.properties['compatibility_issues'].append(error_msg)
            return False
            
        # Get accumulated modules from state if it exists
        accumulated_modules = 0
        if 'accumulated_modules' in ram.properties:
            accumulated_modules = ram.properties['accumulated_modules']
        
        # Calculate total number of modules including accumulated modules
        total_modules = len(ram_modules) + accumulated_modules
        
        # Check if total number of modules exceeds available slots
        if total_modules > mb_memory_slots:
            error_msg = f"Total RAM modules ({total_modules}) exceeds available motherboard slots ({mb_memory_slots})"
            if 'compatibility_issues' not in ram.properties:
                ram.properties['compatibility_issues'] = []
            ram.properties['compatibility_issues'].append(error_msg)
            return False
            
        return True

    def _check_psu_compatibility(self, psu: Component, all_components: Dict[str, Component]) -> bool:
        """Check if PSU can handle the power requirements of all components."""
        psu_wattage = psu.properties.get('wattage')
        total_power_requirement = 0
        
        for component in all_components.values():
            if 'power_requirement' in component.properties:
                total_power_requirement += component.properties['power_requirement']
                
        required_wattage = total_power_requirement * 1.2  # 20% buffer
        
        return psu_wattage >= required_wattage

    def _check_cooling_case_compatibility(self, cooling: Component, case: Component) -> bool:
        """Check if cooling solution fits in the case."""
        cooling_height = cooling.properties.get('height')
        case_max_cooling_height = case.properties.get('max_cooling_height')
        
        if cooling_height > case_max_cooling_height:
            return False
            
        return True

    def _check_motherboard_case_compatibility(self, motherboard: Component, case: Component) -> bool:
        """Check if motherboard form factor is compatible with case."""
        mb_form_factor = motherboard.properties.get('form_factor')
        case_form_factors = case.properties.get('supported_form_factors', [])
        
        return mb_form_factor in case_form_factors

    def _check_storage_motherboard_compatibility(self, storage: Component, motherboard: Component) -> bool:
        """Check if storage device is compatible with motherboard interfaces."""
        storage_interface = storage.properties.get('interface')
        mb_storage_interfaces = motherboard.properties.get('storage_interfaces', [])
        
        return storage_interface in mb_storage_interfaces

    def _check_network_motherboard_compatibility(self, network_card: Component, motherboard: Component) -> bool:
        """Check if network card is compatible with motherboard expansion slots."""
        card_interface = network_card.properties.get('interface')
        mb_expansion_slots = motherboard.properties.get('expansion_slots', [])
        
        return card_interface in mb_expansion_slots

    def _check_sound_motherboard_compatibility(self, sound_card: Component, motherboard: Component) -> bool:
        """Check if sound card is compatible with motherboard expansion slots."""
        card_interface = sound_card.properties.get('interface')
        mb_expansion_slots = motherboard.properties.get('expansion_slots', [])
        
        return card_interface in mb_expansion_slots

    def _check_fan_controller_case_compatibility(self, controller: Component, case: Component) -> bool:
        """Check if fan controller is compatible with case form factor."""
        controller_form_factor = controller.properties.get('form_factor')
        case_form_factors = case.properties.get('fan_controller_form_factors', [])
        
        return controller_form_factor in case_form_factors

    def _check_ups_psu_compatibility(self, ups: Component, psu: Component) -> bool:
        """Check if UPS can handle the power supply's requirements."""
        ups_capacity = ups.properties.get('capacity_w')
        psu_wattage = psu.properties.get('wattage')
        
        return ups_capacity >= psu_wattage * 1.2  # 20% buffer

    def _check_os_memory_compatibility(self, os: Component, memory: Component) -> bool:
        """Check if operating system is compatible with memory configuration."""
        os_max_memory = os.properties.get('max_memory')
        memory_capacity = memory.properties.get('capacity')
        
        return os_max_memory >= memory_capacity
