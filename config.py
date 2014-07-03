import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    conf.registerPlugin('SupySQSMessenger', True)

SupySQSMessenger = conf.registerPlugin('SupySQSMessenger')
conf.registerChannelValue(
    SupySQSMessenger,
    'enable',
    registry.Boolean(
        'False',
        """Enable displaying messages from SupySQSMessenger in channel?"""
    )
)
