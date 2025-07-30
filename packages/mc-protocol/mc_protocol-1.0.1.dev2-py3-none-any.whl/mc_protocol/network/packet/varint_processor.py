from struct import pack
class VarIntProcessor:
    # 遵循算法:varint  参考博客:https://blog.csdn.net/weixin_43708622/article/details/111397322
    @staticmethod
    def packVarInt(value: int) -> bytes:
        buf = bytearray()
        while True:
            byte = value & 0x7F
            value >>= 7
            buf.append(byte | (0x80 if value > 0 else 0))
            if value == 0:
                break
        return bytes(buf)
    @staticmethod
    def readVarInt(data: bytes, offset: int = 0) -> tuple[int, int]:
        result = 0
        shift = 0
        while True:
            if offset >= len(data):
                raise ValueError("Invalid VarInt packet.")
            byte = data[offset]
            offset += 1
            result |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
            if shift > 28:
                raise ValueError("VarInt too large")
        return result, offset

    # 生成握手包
    def packModernServerPingHandshake(host: str, port: int, protocolNum: int):
        handshake = (
            b"\x00" +
            VarIntProcessor.packVarInt(protocolNum) +
            VarIntProcessor.packVarInt(len(host)) +  
            host.encode() +
            pack(">H", port) +
            b'\x01'
        )
        return handshake, VarIntProcessor.packVarInt(len(handshake))
    

