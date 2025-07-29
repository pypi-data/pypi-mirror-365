from typing import Any, Optional

from rclpy.node import Node
import ros2_numpy

from ..core.metadata import PoolMetadata
from  ..core.producer import TensorProducer
from cyclonedds.domain import DomainParticipant

class ROSTensorProducer:
    """
    A producer that connects to a ROS topic and publishes tensor data.
    
    This class extends the TensorProducer to handle ROS-specific logic.
    """
    def __init__(self, 
        pool_metadata: PoolMetadata,
        node: Node,
        ros_topic: str,
        ros_msg_type: Any,
        qos: int = 10,      # ROS qos settings
        keep_last: int = 10,
        dds_participant: Optional[DomainParticipant] = None
    ):
        self.node = node
        self.ros_msg_type = ros_msg_type
        self._pub = self.node.create_publisher(
            ros_msg_type,
            ros_topic,
            qos_profile=qos
        )
        self.tensor_producer = TensorProducer(
            pool_metadata=pool_metadata,
            keep_last=keep_last,
            dds_participant=dds_participant  # ROS does not use DDS directly
        )

    def put(self, data, *args, **kwargs) -> None:
        """
        Publish tensor data to the ROS topic AND update the tensor pool.

        Args:
            data (np.array | torch.Tensor): The tensor data to publish.
        """
        self.tensor_producer.put(data)
        data = self.tensor_producer.backend.mixin.to_numpy(data)
        msg = ros2_numpy.msgify(self.ros_msg_type, data, *args, **kwargs)
        self._pub.publish(msg)

    def cleanup(self) -> None:
        self.tensor_producer.cleanup()
        self.node.destroy_publisher(self._pub)