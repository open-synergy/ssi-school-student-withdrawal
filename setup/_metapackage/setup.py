import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-school-student-withdrawal",
    description="Meta package for open-synergy-ssi-school-student-withdrawal Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_school_student_withdrawal',
        'odoo14-addon-ssi_school_student_withdrawal_operating_unit',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
