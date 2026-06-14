from django.db import models

from estudantes.models.estudantes import Estudante
from projetos.models.projeto import Projeto
from turmas.models.turmas import Turma


class RelatorioEstudante(models.Model):
    estudante = models.ForeignKey(
        Estudante,
        on_delete=models.CASCADE,
        related_name='relatorios',
    )
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='relatorios',
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='relatorios',
    )
    descricao = models.TextField(help_text='Descrição das atividades realizadas pelo estudante no projeto')
    data_envio = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'relatorios_estudantes'
        verbose_name = 'Relatório do Estudante'
        verbose_name_plural = 'Relatórios dos Estudantes'
        unique_together = ('estudante', 'projeto')
        ordering = ['-data_envio']

    def __str__(self):
        return f'Relatório — {self.estudante} / {self.projeto}'
