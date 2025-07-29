# external package imports.
from abc import abstractmethod
from io import BytesIO

# our package imports.
from .sipacket import SIPacket

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIFormatter:
    """
    Responsible for formatting and writing a packet.

    This abstract class defines several methods which are intended
    to preprocess a packet and subsequently write it to a stream.
    The process of preprocessing (or compiling) and writing a packet
    can either be executed with a single step by calling the Format
    method or with two steps by calls to Compile and Write.

    Threadsafety:
        This class and subclasses thereof are not guaranteed to be thread-safe.
    """

    @abstractmethod
    def Compile(self, packet:SIPacket) -> int:
        """
        Preprocesses (or compiles) a packet and returns the required
        size for the compiled result.

        Args:
            packet (SIPacket):
                The packet to compile.

        Raises:
            NotImplementedError:
                Raised if the method is not implemented in an inheriting class.

        Returns:
            The size for the compiled result.

        To write a previously compiled packet, call the Write method.
        Derived classes are intended to compile the supplied packet
        and return the required size for the compiled result.
        """
        raise NotImplementedError()


    def Format(self, packet:SIPacket, stream:BytesIO) -> None:
        """
        Compiles a packet and writes it to a stream.  

        Args:
            packet (SIPacket):
                The packet to compile.
            stream (BytesIO):
                The stream to write the packet to.

        Raises:
            IOException:
                An I/O error occurred while trying to write the compiled packet.

        This non-abstract method simply calls the Compile method with
        the supplied packet object and then the Write method with
        the supplied stream object.
        """
        self.Compile(packet)
        self.Write(stream)


    @abstractmethod
    def Write(self, stream:BytesIO) -> None:
        """
        Writes a previously compiled packet to the supplied stream.

        Args:
            stream (BytesIO):
                The stream to write the packet to.

        Raises:
            IOException:
                An I/O error occurred while trying to write the compiled packet.
            NotImplementedError:
                Raised if the method is not implemented in an inheriting class.

        This method is intended to write a previously compiled packet
        (see Compile) to the supplied stream object. If the return
        value of the Compile method was 0, nothing is written.
        """
        raise NotImplementedError()
