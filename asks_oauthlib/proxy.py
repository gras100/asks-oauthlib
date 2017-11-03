class MappedAttributesProxy(object):
    '''
    Creates a proxy for a source object with attributes mapped per
    the given kwargs.

    e.g. if a is an instance of Class A which has properties prop1
    and prop2, then MappedAttributesProxy(a,new_prop=prop1) will
    have properties prop1 and new_prop mapping to prop1 and prop2
    respectively.

    This may be quite dangerous as edge cases not dealt with or
    looked into.
    '''
    #@classmethod
    #def is_magic(cls,key):
    #    return (key.startswith('__') and
    #            key.endswith('__'))

    def __getattribute__(self,name):
        source = object.__getattribute__(self,'_proxy_source')
        if name in object.__getattribute__(self,'_proxy_block'):
            msg = 'Proxy2({}) source attribute {} blocked.'
            raise AttributeError(msg.format(type(source),name))
        map_ = object.__getattribute__(self,'_proxy_map')
        return = getattr(source,map_.get(name,name))

    def __setattr__(self,name,value):
        source = object.__getattribute__(self,'_proxy_source')
        map_ = object.__getattribute__(self,'_proxy_map')
        setattr(source,map_.get(name,name),value)

    def __init__(self,source,**kwargs):
        object.__setattr__(self,'_proxy_source',source)
        object.__setattr__(self,'_proxy_map',kwargs)
        object.__setattr__(self,'_proxy_block',set(kwargs.values()))