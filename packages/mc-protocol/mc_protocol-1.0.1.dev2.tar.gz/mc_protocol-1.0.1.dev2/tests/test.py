from utils.version.version import MinecraftVersion, isNewer
from utils.version.manifest_version import ManifestVersion
from utils.color import Color
from mc_protocol.network.ping.modern_pinger import ModernPinger
from mc_protocol.network.packet.varint_processor import VarIntProcessor

mani = ManifestVersion("./tests/version_manifest.json")
print(mani.getLatestVersion())