from rest_framework import serializers

from relatorios.models.relatorio import RelatorioEstudante


class RelatorioEstudanteSerializer(serializers.ModelSerializer):
    estudante_nome = serializers.CharField(source='estudante.usuario.nome', read_only=True)
    estudante_matricula = serializers.CharField(source='estudante.matricula', read_only=True)
    estudante_curso = serializers.CharField(source='estudante.curso', read_only=True)
    projeto_nome = serializers.CharField(source='projeto.nome', read_only=True)
    turma_nome = serializers.CharField(source='turma.nome', read_only=True)

    class Meta:
        model = RelatorioEstudante
        fields = (
            'id',
            'estudante',
            'estudante_nome',
            'estudante_matricula',
            'estudante_curso',
            'projeto',
            'projeto_nome',
            'turma',
            'turma_nome',
            'descricao',
            'data_envio',
            'data_atualizacao',
        )
        read_only_fields = (
            'id',
            'estudante',
            'estudante_nome',
            'estudante_matricula',
            'estudante_curso',
            'projeto_nome',
            'turma_nome',
            'data_envio',
            'data_atualizacao',
        )


class EnviarRelatorioSerializer(serializers.Serializer):
    projeto_id = serializers.IntegerField()
    turma_id = serializers.IntegerField()
    descricao = serializers.CharField(min_length=20)
