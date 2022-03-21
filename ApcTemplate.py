from string import Template


class ApcTemplate(Template):
    Template.delimiter = "**"
    # Template.pattern

    def __init__(self, template):
        super(ApcTemplate, self).__init__(template)


#    super(ApcTemplate, self).delimiter

if __name__ == '__main__':
    t = ApcTemplate("%1% %n%s%d %dsf%")

    print(t.substitute({"alal": 1}))
    print(t.pattern)
