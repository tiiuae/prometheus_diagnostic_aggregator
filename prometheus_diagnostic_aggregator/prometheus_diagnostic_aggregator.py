# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# flake8: noqa
import rclpy
from rclpy.node import Node
import prometheus_client
from prometheus_client import Info, Enum, Gauge, Counter

from builtin_interfaces.msg import Time
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue

class Component():
    """
    A class to represent a component.

    ...

    Attributes
    ----------
    component_name : str
        The name of the component given in the DiagnosticStatus.name
    metric_prefix : str
        The prefix of the metrics. If not given, it is set to the component_name.
    info : Info
        The prometheus info object. Used for the non-gauge values.
    status : Enum
        The prometheus enum object. Used for the status. Updated by DiagnosticStatus.level
    counters : dict
        The prometheus counter objects. The local counter is updated by the increment.
    gauges : dict
        The prometheus gauge objects. Used for the gauges.
    info_dict : dict
        The dictionary of the info values. Used for the info.
    
    Methods
    -------
    processDiagnostic(stamp, msg: DiagnosticStatus):
        Processes the diagnostic message. Stamp is used for the last_update_received gauge
    byteToStatusStr(level):
        Converts the level given as byte to a enum states.
    """
    def __init__(self, component_name, metric_prefix = ""):
        self.info = Info(component_name, component_name)
        self.status = Enum(component_name, component_name, states=["OK", "WARN", "ERROR", "STALE"])
        self.counters = {}
        self.gauges = {}
        self.info_dict = {}
        self.component_name = component_name
        self.metric_prefix = metric_prefix
        if self.metric_prefix == "":
            self.metric_prefix = self.component_name + ":"
        self.counters["last_update_received"] = Gauge(self.metric_prefix+"last_update_received", "Last update received time")

    def byteToStatusStr(self, level):
        """ Converts the level given as byte to a enum states. """
        if (level == b'\x00'):
            return "OK"
        elif (level == b'\x01'):
            return "WARN"
        elif (level == b'\x02'):
            return "ERROR"
        elif (level == b'\x03'):
            return "STALE"

    def processDiagnostic(self, stamp, msg: DiagnosticStatus):
        """ Processes the diagnostic message. Stamp is used for the last_update_received gauge """
        for value in msg.values:
            metric_type = value.key.split("/")[0]
            metric_name = value.key.split("/")[1]
            if (metric_type == "gauge"):
                if (metric_name in self.gauges.keys()):
                    self.gauges[metric_name].set(value.value)
                else:
                    self.gauges[metric_name] = Gauge(self.metric_prefix+metric_name, metric_name)
            elif (metric_type == "counter"):
                if (metric_name in self.counters.keys()):
                    # Even though they are counter, they need to be gauge to be able to set them
                    self.counters[metric_name].inc(value.value - self.counters[metric_name].get())
                else:
                    self.counters[metric_name] = Counter(self.metric_prefix+metric_name, metric_name)
            elif (metric_type == "info"):
                self.info_dict[metric_name] = value.value
        self.counters["last_update_received"].set(stamp.sec + stamp.nanosec/1000000000)
        self.info.info(self.info_dict)
        self.status.state(self.byteToStatusStr(msg.level))

class PrometheusDiagnosticAggregator(Node):
    def __init__(self):
        super().__init__('prometheus_diagnostic_aggregator')
        self.subscription = self.create_subscription(
            DiagnosticArray,
            '/diagnostics',
            self.diagnosticsCallback,
            10)
        self.subscription  # prevent unused variable warning
        self.components = {}

    def diagnosticsCallback(self, msg):
        for diag_status in msg.status:
            component_name = msg.status[0].name.replace(" ", "")
            if (component_name not in self.components):
                self.components[component_name] = Component(component_name)
            self.components[component_name].processDiagnostic(msg.header.stamp, diag_status)

def main(args=None):
    rclpy.init(args=args)
    prometheus_client.start_http_server(9101)

    prometheus_diagnostic_aggregator = PrometheusDiagnosticAggregator()

    rclpy.spin(prometheus_diagnostic_aggregator)

    prometheus_diagnostic_aggregator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
