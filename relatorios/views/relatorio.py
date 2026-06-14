from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from aplicacoes.models.aplicacao import Aplicacao
from autenticacao.enums.roles import Role
from estudantes.models.estudantes import Estudante
from estudantes.models.estudantes_turmas import EstudanteTurma
from professores.models.professores import Professor
from projetos.models.projeto import Projeto
from relatorios.models.relatorio import RelatorioEstudante
from relatorios.serializers.relatorio import RelatorioEstudanteSerializer, EnviarRelatorioSerializer
from turmas.models.turmas import Turma
from turmas.models.turmas_professor import TurmaProfessor


@extend_schema_view(
    retrieve=extend_schema(responses={200: RelatorioEstudanteSerializer}),
)
class RelatorioViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = RelatorioEstudanteSerializer

    def get_queryset(self):
        return RelatorioEstudante.objects.select_related(
            'estudante__usuario',
            'estudante__universidade',
            'projeto',
            'turma',
        ).all()

    @extend_schema(
        request=EnviarRelatorioSerializer,
        responses={201: RelatorioEstudanteSerializer, 200: RelatorioEstudanteSerializer},
    )
    @action(detail=False, methods=['post'], url_path='enviar')
    def enviar(self, request):
        try:
            estudante = Estudante.objects.get(usuario=request.user)
        except Estudante.DoesNotExist:
            return Response(
                {'detail': 'Perfil de estudante não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EnviarRelatorioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            projeto = Projeto.objects.get(pk=data['projeto_id'])
        except Projeto.DoesNotExist:
            return Response(
                {'detail': 'Projeto não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if projeto.status != Projeto.Status.CONCLUIDO:
            return Response(
                {'detail': 'O relatório só pode ser enviado após a conclusão do projeto.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            turma = Turma.objects.get(pk=data['turma_id'])
        except Turma.DoesNotExist:
            return Response(
                {'detail': 'Turma não encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        inscricao_aceita = EstudanteTurma.objects.filter(
            estudante=estudante,
            turma=turma,
            status=EstudanteTurma.Status.ACEITO,
        ).exists()

        if not inscricao_aceita:
            return Response(
                {'detail': 'Você não possui inscrição aceita nesta turma.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        participou = Aplicacao.objects.filter(
            turma=turma,
            atividade__projeto=projeto,
            status=Aplicacao.Status.ACEITA,
        ).exists()

        if not participou:
            return Response(
                {'detail': 'Esta turma não possui participação aceita neste projeto.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        relatorio, created = RelatorioEstudante.objects.update_or_create(
            estudante=estudante,
            projeto=projeto,
            defaults={
                'turma': turma,
                'descricao': data['descricao'],
            },
        )

        response_serializer = RelatorioEstudanteSerializer(relatorio)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @extend_schema(responses={200: RelatorioEstudanteSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='meus-relatorios')
    def meus_relatorios(self, request):
        try:
            estudante = Estudante.objects.get(usuario=request.user)
        except Estudante.DoesNotExist:
            return Response(
                {'detail': 'Perfil de estudante não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        relatorios = RelatorioEstudante.objects.filter(
            estudante=estudante,
        ).select_related('projeto', 'turma', 'estudante__usuario')

        response_serializer = self.get_serializer(relatorios, many=True)
        return Response(response_serializer.data)

    @extend_schema(responses={200: RelatorioEstudanteSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='turma/(?P<turma_id>[^/.]+)')
    def por_turma(self, request, turma_id=None):
        if request.user.role != Role.PROFESSOR:
            return Response(
                {'detail': 'Apenas professores podem acessar relatórios por turma.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            professor = Professor.objects.get(usuario=request.user)
        except Professor.DoesNotExist:
            return Response(
                {'detail': 'Perfil de professor não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        vinculado = TurmaProfessor.objects.filter(
            professor=professor,
            turma_id=turma_id,
        ).exists()

        if not vinculado:
            return Response(
                {'detail': 'Você não é professor desta turma.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        relatorios = RelatorioEstudante.objects.filter(
            turma_id=turma_id,
        ).select_related(
            'estudante__usuario',
            'estudante__universidade',
            'projeto',
            'turma',
        )

        projeto_id = request.query_params.get('projeto_id')
        if projeto_id:
            relatorios = relatorios.filter(projeto_id=projeto_id)

        response_serializer = self.get_serializer(relatorios, many=True)
        return Response(response_serializer.data)
